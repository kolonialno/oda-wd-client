import os
from datetime import datetime
from typing import Any, Iterator
from urllib.parse import urljoin

from suds import client as suds_client
from suds import sudsobject, wsse
from suds.plugin import MessagePlugin

from oda_wd_client.base.logging import log


class SudsHax(MessagePlugin):
    def marshalled(self, context):
        # Ugly hack: Add namespace to ID attribute (ref.
        # https://stackoverflow.com/a/5730868/6866905)
        root = context.envelope.getChild("Body")

        def recurse(obj):
            for attr in obj.attributes:
                attr.prefix = obj.parent.prefix
            if obj.children:
                for child in obj.children:
                    recurse(child)

        recurse(root)


class SudsLog(MessagePlugin):
    """
    Write all responses and requests to files during development

    Inspired by https://www.guguweb.com/2019/12/11/how-to-log-raw-xml-requests-and-responses-in-suds/
    """

    def __init__(self, location):
        self.location = location
        if not os.path.exists(location):
            os.makedirs(location)

    def pretty_log(self, xml_content, direction):
        try:
            file_path = os.path.join(
                self.location, f"suds-log-{datetime.now()}-{direction}.xml"
            )
            with open(file_path, "wb") as f:
                f.write(xml_content)
        except Exception as e:
            log("warning", f"Cannot log XML ({e})")

    def sending(self, context):
        self.pretty_log(context.envelope, "send")

    def received(self, context):
        self.pretty_log(context.reply, "receive")


# Using a singleton to hold all of our client instances to avoid re-initiation during app lifecycle. Changing the
# credentials requires us to reload the app anyway.
_workday_clients: dict[str, suds_client.Client] = {}


class WorkdayClient:
    """
    An abstraction on top of the Suds SOAP client to give us an interface into
    Workday that's been instantiated with our own settings

    Relevant docs: https://community.workday.com/articles/628676
    """

    # Each SOAP service must be instantiated individually, and we need more than one...
    _services: list[str] = [
        "Human_Resources",
        "Staffing",
        "Financial_Management",
        "Resource_Management",
    ]

    service: str

    def __init__(
        self,
        base_url: str,
        tenant_name: str,
        username: str,
        password: str,
        lazy_init: bool = True,
        log_location: str | None = None,
    ) -> None:
        self._auth_base_url = base_url
        self._auth_tenant_name = tenant_name
        self._auth_username = username
        self._auth_password = password
        self._log_location = log_location
        # If we do lazy init, we only initialize each service when they're first needed, since there's an overhead
        # with the init process
        if not lazy_init:
            for service in self._services:
                self._init_service_client(service)
        assert (
            self.service
        ), "`WorkdayClient` must be subclassed, and all subclasses must have `.service` set"

    def _init_service_client(self, service: str) -> None:
        if service not in _workday_clients:
            url = self._get_client_url(service)
            _workday_clients[service] = self._setup_client(url)

    def _get_client_url(self, service: str) -> str:
        return urljoin(
            self._auth_base_url,
            f"/ccx/service/{self._auth_tenant_name}/{service}/v38.1?wsdl",
        )

    def _setup_client(self, url: str) -> suds_client.Client:
        """
        Create client instance with secrets and config
        """
        plugins = [SudsHax()]
        if self._log_location:
            plugins.append(SudsLog(self._log_location))
        client = suds_client.Client(url, plugins=plugins)
        security = wsse.Security()
        token = wsse.UsernameToken(
            f"{self._auth_username}@{self._auth_tenant_name}",
            self._auth_password,
        )
        token.setnonce()
        token.setcreated()
        security.tokens.append(token)
        client.set_options(wsse=security, prettyxml=True)
        return client

    def get_client(self, service: str) -> suds_client.Client:
        """
        Instantiate client if it hasn't been instantiated, else just get client instance
        """
        if service not in _workday_clients:
            self._init_service_client(service)
        return _workday_clients[service]

    def _request(self, method_name: str, *args, **kwargs) -> sudsobject.Object:
        """
        Wrapper to call service methods on client instance
        """
        method = getattr(self.get_client(self.service).service, method_name)
        return method(*args, **kwargs)

    def _get_paginated(
        self,
        method_name: str,
        results_key: str,
        filters: dict[str, Any] | None = None,
        per_page: int = 100,
        extra_request_kwargs: dict[str, Any] | None = None,
    ) -> Iterator[sudsobject.Object]:
        extra_request_kwargs = extra_request_kwargs or {}
        page = 1
        max_page = None
        while max_page is None or page <= max_page:
            str_max_page = "Unknown"
            if max_page:
                str_max_page = int(max_page)
            log(
                "info",
                f"Getting page {page} of {str_max_page}",
            )
            _filter = self.factory("ns0:Response_FilterType")

            if filters:
                for key, val in filters.items():
                    setattr(_filter, key, val)

            _filter.Page = page
            _filter.Count = per_page
            response = self._request(
                method_name, Response_Filter=_filter, **extra_request_kwargs
            )

            # Response_Results / Response_Data might be wrapped in a list, if so, pick out the object
            # Double check that they only have one item
            response_results = response.Response_Results

            if isinstance(response_results, list):
                assert (
                    len(response_results) == 1
                ), "If Response_Results is a list, it should only have one item"
                response_results = response_results[0]

            # If we get no results, we won't have any response data attribute, so we need to do an early return
            #  before attempting to access that data.
            if int(response_results.Total_Results) == 0:
                log("info", "No results")
                return

            response_data = response.Response_Data

            if isinstance(response_data, list):
                assert (
                    len(response_data) == 1
                ), "If Response_Data is a list, it should only have one item"
                response_data = response_data[0]

            max_page = response_results.Total_Pages
            for result in getattr(response_data, results_key):
                yield result

            page += 1

    def factory(self, name: str) -> sudsobject.Object:
        """
        Convenience wrapper
        """
        return self.get_client(self.service).factory.create(name)

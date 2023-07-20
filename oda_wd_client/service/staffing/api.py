from typing import Iterable

from suds import sudsobject

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.tools import suds_to_dict
from oda_wd_client.service.staffing.types import Document
from oda_wd_client.service.staffing.utils import workday_document_to_pydantic


class Staffing(WorkdayClient):
    service = "Staffing"

    def put_document(self, *args, **kwargs) -> sudsobject.Object:
        """
        Upload a new document to WD
        """
        method = "Put_Worker_Document"
        return self._request(method, *args, Add_Only=True, **kwargs)

    def get_documents(
        self, raw_objects=False
    ) -> Iterable[Document | sudsobject.Object]:
        """
        Get all documents (as we can't filter on user...)
        """
        method = "Get_Worker_Documents"

        _response_group = self.factory("ns0:Worker_Document_Response_GroupType")
        _response_group.Include_Worker_Document_Data = False
        extra_request_kwargs = {
            "Worker_Document_Response_Group": _response_group,
        }
        docs = self._get_paginated(
            method,
            "Worker_Documents",
            per_page=25,
            extra_request_kwargs=extra_request_kwargs,
        )
        for doc in docs:
            if raw_objects:
                yield doc
            else:
                yield workday_document_to_pydantic(suds_to_dict(doc))

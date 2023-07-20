from typing import Iterator

from suds import sudsobject

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.tools import suds_to_dict
from oda_wd_client.service.resource_management.types import Supplier, SupplierInvoice
from oda_wd_client.service.resource_management.utils import (
    pydantic_supplier_invoice_to_workday,
    workday_supplier_to_pydantic,
)


class ResourceManagement(WorkdayClient):
    service = "Resource_Management"

    def get_suppliers(
        self, return_suds_object=False
    ) -> Iterator[sudsobject.Object | Supplier]:
        method = "Get_Suppliers"
        results = self._get_paginated(method, "Supplier")
        for supplier in results:
            yield supplier if return_suds_object else workday_supplier_to_pydantic(
                suds_to_dict(supplier)
            )

    def get_supplier_invoices(
        self, return_suds_object=False
    ) -> Iterator[sudsobject.Object | SupplierInvoice]:
        method = "Get_Supplier_Invoices"
        results = self._get_paginated(method, "Supplier_Invoice")
        for supplier in results:
            yield supplier if return_suds_object else workday_supplier_to_pydantic(
                suds_to_dict(supplier)
            )

    def submit_supplier_invoice(self, invoice: SupplierInvoice) -> sudsobject.Object:
        method = "Submit_Supplier_Invoice"
        request = self.factory("ns0:Submit_Supplier_Invoice_Request")
        request.Supplier_Invoice_Data = pydantic_supplier_invoice_to_workday(
            invoice, self
        )
        return self._request(
            method, Supplier_Invoice_Data=request.Supplier_Invoice_Data
        )

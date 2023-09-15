from typing import Iterator

from suds import sudsobject

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.tools import suds_to_dict
from oda_wd_client.service.resource_management.exceptions import NoSupplierID
from oda_wd_client.service.resource_management.types import Supplier, SupplierInvoice
from oda_wd_client.service.resource_management.utils import (
    pydantic_supplier_invoice_to_workday,
    workday_supplier_invoice_to_pydantic,
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
            try:
                yield supplier if return_suds_object else workday_supplier_to_pydantic(
                    suds_to_dict(supplier)
                )
            except NoSupplierID:
                # We'll skip suppliers without an ID
                pass

    def get_supplier_invoices(
        self, return_suds_object=False
    ) -> Iterator[sudsobject.Object | SupplierInvoice]:
        method = "Get_Supplier_Invoices"
        results = self._get_paginated(method, "Supplier_Invoice")
        for invoice in results:
            yield invoice if return_suds_object else workday_supplier_invoice_to_pydantic(
                suds_to_dict(invoice)
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

    def cancel_supplier_invoice(self, invoice_ref_id: str):
        """
        Cancel an invoice in Workday

        :param invoice_ref_id:
        :return:
        """
        method = "Cancel_Supplier_Invoice"
        ref_obj = self.factory("ns0:Supplier_InvoiceObjectType")
        id_obj = self.factory("ns0:Supplier_InvoiceObjectIDType")
        id_obj._type = "Supplier_Invoice_Reference_ID"
        id_obj.value = invoice_ref_id
        ref_obj.ID.append(id_obj)
        return self._request(method, Supplier_Invoice_Reference=ref_obj)

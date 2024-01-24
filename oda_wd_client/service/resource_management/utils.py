from typing import Any

from suds import sudsobject

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.utils import get_id_from_list
from oda_wd_client.service.financial_management.types import (
    Company,
    CostCenterWorktag,
    Currency,
    SpendCategory,
)
from oda_wd_client.service.resource_management.exceptions import NoSupplierID
from oda_wd_client.service.resource_management.types import (
    PrepaidAmortizationType,
    Supplier,
    SupplierInvoice,
    SupplierInvoiceAdjustment,
    SupplierInvoiceLine,
    SupplierStatus,
    TaxApplicability,
    TaxCode,
    TaxOption,
    TaxRate,
    TaxRateOptionsData,
    TaxRecoverability,
)


def _get_account_data_from_dict(data: dict) -> dict:
    """
    Retrieve bank account data from a Settlement Account Widget Data dict

    The keys in the returned dict are defined by the Supplier pydantic model
    """
    settlement_data = data.get("Settlement_Account_Data", None)
    # TODO: Add filtering to ensure we use the correct account
    used = settlement_data[0] if settlement_data else {}

    ret = {
        "iban": used.get("IBAN", None),
        "bank_account": used.get("Bank_Account_Number", None),
    }

    return ret


def _get_contact_data_from_dict(data: dict) -> dict:
    """
    Retrieve contact information from a Contact Data dict

    The keys in the returned dict are defined by the Supplier pydantic model
    """
    ret = {}
    address_info = data.get("Address_Data", None)
    phone_info = data.get("Phone_Data", None)
    email_info = data.get("Email_Address_Data", None)
    url_info = data.get("Web_Address_Data", None)

    if address_info:
        current = sorted(
            address_info, reverse=True, key=lambda addr: addr["_Effective_Date"]
        )[0]
        # We'll just use the pre-formatted address from Workday as value
        ret["address"] = current["_Formatted_Address"].replace("&#xa;", "\n")

    if phone_info:
        # TODO: Decide if we need to filter on which number to use
        ret["phone"] = phone_info[0]["_E164_Formatted_Phone"]

    if email_info:
        # TODO: Decide if we need to filter on which email address to use
        ret["email"] = email_info[0]["Email_Address"]

    if url_info:
        # TODO: Decide if we need to filter on which URL to use
        ret["url"] = url_info[0]["Web_Address"]

    return ret


def workday_supplier_to_pydantic(data: dict) -> Supplier:
    """
    Parse a suds dict representing a supplier from Workday and return a Supplier pydantic instance
    """
    sup_data = data["Supplier_Data"]
    sup_id = sup_data.get("Supplier_ID", None)
    if not sup_id:
        raise NoSupplierID()
    primary_tax_id = None
    tax_id_data = sup_data.get("Tax_ID_Widget_Data", {}).get("Tax_ID_Data", [])
    for item in tax_id_data:
        # We can get a widget data item that has no Tax ID Text attribute
        if item["Primary_Tax_ID"] and "Tax_ID_Text" in item:
            primary_tax_id = item["Tax_ID_Text"]
    account_data = _get_account_data_from_dict(
        sup_data.get("Settlement_Account_Widget_Data", {})
    )
    contact_data = _get_contact_data_from_dict(
        sup_data["Business_Entity_Data"].get("Contact_Data", {})
    )
    currency_ref = sup_data.get("Currency_Reference", None)
    status_ref = None
    for status_line in sup_data.get("Supplier_Status_Data", []):
        _ref = SupplierStatus.from_id_list(status_line["Status_Reference"]["ID"])
        if _ref:
            status_ref = _ref

    return Supplier(
        workday_id=sup_id,
        reference_id=sup_data.get("Supplier_Reference_ID", None),
        name=sup_data["Supplier_Name"],
        status=status_ref,
        payment_terms=get_id_from_list(
            sup_data.get("Payment_Terms_Reference", {}).get("ID", []),
            "Payment_Terms_ID",
        ),
        primary_tax_id=primary_tax_id,
        # Currency_ID _should_ be in accordance with ISO 4217
        currency=get_id_from_list(currency_ref["ID"], "Currency_ID")
        if currency_ref
        else None,
        **contact_data,
        **account_data,
    )


def _workday_invoice_line_to_pydantic(data: dict, order: int) -> SupplierInvoiceLine:
    cost_center = None
    # Worktags is a list of tags, each with their own list of IDs
    worktags = data.get("Worktags_Reference", [])
    for tag in worktags:
        _cost_center = CostCenterWorktag.from_id_list(tag["ID"])
        if _cost_center:
            cost_center = _cost_center

    tax_rate_options_data = None
    try:
        tax_option = TaxOption.from_id_list(data["Tax_Option_1_Reference"]["ID"])
        tax_rate = TaxRate.from_id_list(data["Tax_Rate_1_Reference"]["ID"])
        tax_recoverability = TaxRecoverability.from_id_list(
            data["Tax_Recoverability_1_Reference"]["ID"]
        )
        # Need to do type narrowing here to avoid passing on nullable objects to TaxRateOptionsData
        assert tax_option
        assert tax_rate
        assert tax_recoverability
        tax_rate_options_data = TaxRateOptionsData(
            tax_option=tax_option,
            tax_rate=tax_rate,
            tax_recoverability=tax_recoverability,
        )
    except (KeyError, AssertionError):
        pass

    return SupplierInvoiceLine(
        order=order,
        description=data.get("Item_Description", ""),
        tax_rate_options_data=tax_rate_options_data,
        tax_applicability=TaxApplicability.from_id_list(
            data["Tax_Applicability_Reference"]["ID"]
        )
        if "Tax_Applicability_Reference" in data
        else None,
        tax_code=TaxCode.from_id_list(data["Tax_Code_Reference"]["ID"])
        if "Tax_Code_reference" in data
        else None,
        spend_category=SpendCategory.from_id_list(
            data["Spend_Category_Reference"]["ID"]
        )
        if "Spend_Category_Reference" in data
        else None,
        cost_center=cost_center,
        gross_amount=data["Extended_Amount"],
    )


def _get_common_invoice_attributes(inv: dict) -> dict:
    lines = []
    for i, line in enumerate(
        sorted(
            inv["Invoice_Line_Replacement_Data"], key=lambda _line: _line["Line_Order"]
        )
    ):
        lines.append(_workday_invoice_line_to_pydantic(line, i))

    company_ref = get_id_from_list(
        inv["Company_Reference"]["ID"], "Company_Reference_ID"
    )
    currency_ref = get_id_from_list(inv["Currency_Reference"]["ID"], "Currency_ID")
    supplier_ref = get_id_from_list(inv["Supplier_Reference"]["ID"], "Supplier_ID")

    # Type narrowing
    assert company_ref is not None
    assert currency_ref is not None
    assert supplier_ref is not None

    return {
        "company_ref": company_ref,
        "currency_ref": currency_ref,
        "supplier_ref": supplier_ref,
        "lines": lines,
    }


def workday_supplier_invoice_to_pydantic(data: dict) -> SupplierInvoice:
    data_list = data["Supplier_Invoice_Data"]
    assert len(data_list) == 1, "Expecting only one invoice in this dataset"
    inv: dict[str, Any] = data_list[0]

    prepaid_ref = get_id_from_list(
        inv["Prepayment_Release_Type_Reference"]["ID"], "Prepayment_Release_Type_ID"
    )
    common = _get_common_invoice_attributes(inv)

    return SupplierInvoice(
        workday_id=get_id_from_list(
            data["Supplier_Invoice_Reference"]["ID"],
            id_type="Supplier_Invoice_Reference_ID",
        ),
        invoice_number=inv["Invoice_Number"],
        company=Company(workday_id=common["company_ref"]),
        currency=Currency(currency_code=common["currency_ref"]),
        supplier=Supplier(workday_id=common["supplier_ref"]),
        invoice_date=inv["Invoice_Date"],
        due_date=inv["Due_Date_Override"],
        total_amount=inv["Control_Amount_Total"],
        tax_amount=inv["Tax_Amount"],
        prepaid=inv["Prepaid"],
        prepayment_release_type_reference=PrepaidAmortizationType(
            workday_id=getattr(PrepaidAmortizationType.WorkdayID, prepaid_ref)
        )
        if prepaid_ref
        else None,
        lines=common["lines"],
    )


def workday_supplier_invoice_adjustment_to_pydantic(
    data: dict,
) -> SupplierInvoiceAdjustment:
    data_list = data["Supplier_Invoice_Adjustment_Data"]
    assert len(data_list) == 1, "Expecting only one invoice in this dataset"
    inv: dict[str, Any] = data_list[0]

    common = _get_common_invoice_attributes(inv)

    return SupplierInvoiceAdjustment(
        workday_id=get_id_from_list(
            data["Supplier_Invoice_Adjustment_Reference"]["ID"],
            id_type="Supplier_Invoice_Adjustment_Reference_ID",
        ),
        invoice_number=inv["Invoice_Number"],
        company=Company(workday_id=common["company_ref"]),
        currency=Currency(currency_code=common["currency_ref"]),
        supplier=Supplier(workday_id=common["supplier_ref"]),
        adjustment_date=inv["Adjustment_Date"],
        due_date=inv["Due_Date_Override"],
        total_amount=inv["Control_Total_Amount"],
        tax_amount=inv["Tax_Amount"],
        lines=common["lines"],
    )


def _get_wd_invoice_lines_from_invoice(
    client, lines: list[SupplierInvoiceLine]
) -> list[sudsobject.Object]:
    returned_lines = []

    for line in lines:
        wd_line = client.factory("ns0:Supplier_Invoice_Line_Replacement_DataType")
        wd_line.Line_Order = line.order
        wd_line.Quantity = line.quantity
        wd_line.Item_Description = line.description
        # Extended amount is without VAT
        wd_line.Extended_Amount = line.net_amount
        if line.spend_category:
            wd_line.Spend_Category_Reference = line.spend_category.wd_object(client)

        # Tax options
        tax_opts = line.tax_rate_options_data
        if tax_opts:
            wd_tax = client.factory("ns0:Tax_Rate_Options_DataType")
            wd_tax.Tax_Rate_1_Reference = tax_opts.tax_rate.wd_object(client)
            wd_tax.Tax_Recoverability_1_Reference = (
                tax_opts.tax_recoverability.wd_object(client)
            )
            wd_tax.Tax_Option_1_Reference = tax_opts.tax_option.wd_object(client)
            wd_line.Tax_Rate_Options_Data = wd_tax

        # Tax code
        if line.tax_applicability:
            wd_line.Tax_Applicability_Reference = line.tax_applicability.wd_object(
                client
            )
        if line.tax_code:
            wd_line.Tax_Code_Reference = line.tax_code.wd_object(client)

        # Worktags
        if line.cost_center:
            wd_line.Worktags_Reference.append(line.cost_center.wd_object(client))

        returned_lines.append(wd_line)

    return returned_lines


def pydantic_supplier_invoice_to_workday(
    invoice: SupplierInvoice | SupplierInvoiceAdjustment, client: WorkdayClient
) -> sudsobject.Object:
    """
    Generate the data that is needed for a for Supplier_Invoice_Data in a call to Submit_Supplier_Invoice,
    or for Supplier_Invoice_Adjustment_Data in a call to Submit_Supplier_Invoice_Adjustment
    """

    # Handle attributes unique to a specific type
    if isinstance(invoice, SupplierInvoice):
        invoice_data = client.factory("ns0:Supplier_Invoice_DataType")
        invoice_data.Invoice_Date = str(invoice.invoice_date)
        invoice_data.Control_Amount_Total = invoice.total_amount
        invoice_data.Prepaid = invoice.prepaid
        invoice_data.Prepayment_Release_Type_Reference = (
            (invoice.prepayment_release_type_reference.wd_object(client))
            if invoice.prepayment_release_type_reference
            else None
        )
    elif isinstance(invoice, SupplierInvoiceAdjustment):
        invoice_data = client.factory("ns0:Supplier_Invoice_Adjustment_DataType")
        invoice_data.Adjustment_Date = str(invoice.adjustment_date)
        invoice_data.Control_Total_Amount = invoice.total_amount
        invoice_data.Adjustment_Reason_Reference = invoice.adjustment_reason.wd_object(
            client
        )
    else:
        raise Exception("Invalid invoice type")

    invoice_data.Submit = invoice.submit
    invoice_data.Locked_in_Workday = invoice.locked_in_workday

    # We want to let workday set the invoice number, but keep the invoice's number for supplier's invoice number
    invoice_data.Invoice_Number = None
    invoice_data.Suppliers_Invoice_Number = invoice.invoice_number
    invoice_data.Company_Reference = invoice.company.wd_object(client)
    invoice_data.Currency_Reference = invoice.currency.wd_object(client)
    invoice_data.Supplier_Reference = invoice.supplier.wd_object(client)
    if invoice.tax_option:
        invoice_data.Default_Tax_Option_Reference = invoice.tax_option.wd_object(client)
    invoice_data.Due_Date_Override = str(invoice.due_date)
    # invoice_data.Tax_Amount = invoice.tax_amount
    # invoice_data.Attachment_Data = _get_wd_attachment_data_from_invoice(invoice)
    invoice_data.Invoice_Line_Replacement_Data = _get_wd_invoice_lines_from_invoice(
        client, invoice.lines
    )
    if invoice.additional_reference_number:
        if not invoice.additional_type_reference:
            raise Exception(
                "If additional_reference_number is set, then additional_type_reference must also be set"
            )
        invoice_data.Additional_Reference_Number = invoice.additional_reference_number
        invoice_data.Additional_Type_Reference = (
            invoice.additional_type_reference.wd_object(client)
        )

    if invoice.external_po_number:
        invoice_data.External_PO_Number = invoice.external_po_number

    if invoice.attachments:
        invoice_data.Attachment_Data = [
            attachment.wd_object(client) for attachment in invoice.attachments
        ]

    return invoice_data

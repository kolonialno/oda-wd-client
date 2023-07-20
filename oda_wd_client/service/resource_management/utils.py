from suds import sudsobject

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.utils import get_id_from_list
from oda_wd_client.service.resource_management.types import (
    Supplier,
    SupplierInvoice,
    SupplierInvoiceLine,
    TaxApplicability,
)

# Mapping the Workday tax ID types to canonical names used by our model
# If the prefixes of this list were ISO 3166-compatible, we could just use those to match to country-specific fields,
# but they're not (see Ireland), so we need a canonical mapping of our own.
TAX_ID_SPEC = {
    "AUT-UID": "tax_id_au",
    "BEL-NOTVA": "tax_id_be",
    "DEU-USTIDNR": "tax_id_de",
    "DNK-MOMS": "tax_id_dk",
    "ESP-IVA": "tax_id_es",
    "FIN-ALV": "tax_id_fi",
    "GBR-VATREGNO": "tax_id_gb",
    "IRE-VATNO": "tax_id_ir",
    "NLD-BTWNR": "tax_id_nl",
    "NOR-VAT": "tax_id_no",
    "SWE-MOMSNR": "tax_id_se",
    "USA-EIN": "tax_id_us",
}


def _get_tax_id_from_dict(data: dict) -> dict:
    """
    Tax IDs, like the Norwegian organization number, are nested deep into the
    response from Workday. We'll attempt to get and flatten those values.
    """
    ret = {}

    for tax_id_type in data.get("Tax_ID_Data", []):
        type_ref_value = get_id_from_list(
            tax_id_type["Tax_ID_Type_Reference"]["ID"], "Tax_ID_Type"
        )
        assert type_ref_value, "Tax ID type is an expected reference in this object"
        type_name = TAX_ID_SPEC[type_ref_value]
        ret[type_name] = tax_id_type["Tax_ID_Text"]

    return ret


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
    tax_id_data = _get_tax_id_from_dict(sup_data.get("Tax_ID_Widget_Data", {}))
    account_data = _get_account_data_from_dict(
        sup_data.get("Settlement_Account_Widget_Data", {})
    )
    contact_data = _get_contact_data_from_dict(
        sup_data["Business_Entity_Data"].get("Contact_Data", {})
    )
    currency_ref = sup_data.get("Currency_Reference", None)

    return Supplier(
        workday_id=sup_data.get("Supplier_ID", None),
        reference_id=sup_data.get("Supplier_Reference_ID", None),
        name=sup_data["Supplier_Name"],
        payment_terms=get_id_from_list(
            sup_data.get("Payment_Terms_Reference", {}).get("ID", []),
            "Payment_Terms_ID",
        ),
        # Currency_ID _should_ be in accordance with ISO 4217
        currency=get_id_from_list(currency_ref["ID"], "Currency_ID")
        if currency_ref
        else None,
        **contact_data,
        **account_data,
        **tax_id_data,
    )


def _get_wd_invoice_lines_from_invoice(client, lines: list[SupplierInvoiceLine]):
    returned_lines = []

    for line in lines:
        wd_line = client.factory("ns0:Supplier_Invoice_Line_Replacement_DataType")
        # wd_tax = client.factory("ns0:Tax_Rate_Options_DataType")
        wd_line.Supplier_Invoice_Line_ID = line.order
        wd_line.Item_Description = line.description
        wd_line.Extended_Amount = line.amount

        # wd_line.Tax_Rate_Options_Data = wd_tax
        test_applicability = TaxApplicability(
            workday_id="NOR_Domestic_Purchase_of_Goods_and_Services"
        )
        wd_line.Tax_Applicability_Reference = test_applicability.wd_object(
            client, "Tax_ApplicabilityObject"
        )
        returned_lines.append(wd_line)

    return returned_lines


def pydantic_supplier_invoice_to_workday(
    invoice: SupplierInvoice, client: WorkdayClient
) -> sudsobject.Object:
    """
    Generate the data that is needed for a for Supplier_Invoice_Data in a call to Submit_Supplier_Invoice
    """
    invoice_data = client.factory("ns0:Supplier_Invoice_DataType")

    # Submit to business process rather than uploading invoice in draft mode
    invoice_data.Submit = True

    # Should not be edited inside Workday, only through API
    invoice_data.Locked_in_Workday = True

    invoice_data.Invoice_Number = invoice.invoice_number
    invoice_data.Company_Reference = invoice.company.wd_object(client, "CompanyObject")
    invoice_data.Currency_Reference = invoice.currency.wd_object(
        client, "CurrencyObject"
    )
    invoice_data.Supplier_Reference = invoice.supplier.wd_object(
        client, "SupplierObject"
    )
    invoice_data.Default_Tax_Option_Reference = invoice.tax_option.wd_object(
        client, "Tax_OptionObject"
    )
    invoice_data.Invoice_Date = str(invoice.invoice_date)
    invoice_data.Due_Date_Override = str(invoice.due_date)
    invoice_data.Control_Amount_Total = invoice.total_amount
    invoice_data.Tax_Amount = invoice.tax_amount
    # invoice_data.Attachment_Data = _get_wd_attachment_data_from_invoice(invoice)
    invoice_data.Invoice_Line_Replacement_Data = _get_wd_invoice_lines_from_invoice(
        client, invoice.lines
    )

    return invoice_data

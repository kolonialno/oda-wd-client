from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel

from oda_wd_client.base.types import (
    File,
    WorkdayCurrency,
    WorkdayCurrencyHighAccuracy,
    WorkdayDate,
    WorkdayReferenceBaseModel,
)
from oda_wd_client.service.financial_management.types import (
    Company,
    CostCenterWorktag,
    Currency,
    ProjectWorktag,
    SpendCategory,
)

# All public imports should be done through oda_wd_client.types.resource_management
__all__: list = []


class TaxApplicability(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Tax_ApplicabilityObjectType  # noqa
    """

    _class_name = "Tax_ApplicabilityObject"
    workday_id: str
    workday_id_type: Literal["Tax_Applicability_ID"] = "Tax_Applicability_ID"
    # Code is human-readable text but not critical, so we default to empty string
    code: str = ""
    taxable: bool = True


class TaxOption(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Tax_OptionObjectType  # noqa
    """

    _class_name = "Tax_OptionObject"
    workday_id: str
    workday_id_type: Literal["Tax_Option_ID"] = "Tax_Option_ID"


class TaxCode(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Tax_CodeObjectType  # noqa
    """

    _class_name = "Tax_CodeObject"
    workday_id: str
    workday_id_type: Literal["Tax_Code_ID"] = "Tax_Code_ID"


class SupplierStatus(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Get_Suppliers.html#Supplier_Status_DataType  # noqa
    """

    class WorkdayID(str, Enum):
        active = "ACTIVE"
        inactive = "INACTIVE"

    _class_name = "Business_Entity_Status_ValueObject"
    workday_id: WorkdayID
    workday_id_type: Literal[
        "Business_Entity_Status_Value_ID"
    ] = "Business_Entity_Status_Value_ID"


class Supplier(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Get_Suppliers.html#SupplierType  # noqa
    """

    _class_name = "SupplierObject"
    workday_id: str
    workday_id_type: Literal["Supplier_ID"] = "Supplier_ID"
    status: SupplierStatus | None = None
    reference_id: str | None = None
    name: str | None = None
    payment_terms: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    url: str | None = None
    currency: str | None = None
    bank_account: str | None = None
    iban: str | None = None
    primary_tax_id: str | None = None


class TaxRate(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Tax_RateObjectType  # noqa
    """

    _class_name = "Tax_RateObject"
    workday_id: str
    workday_id_type: Literal["Tax_Rate_ID"] = "Tax_Rate_ID"


class TaxRecoverability(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Tax_RecoverabilityObjectType  # noqa
    """

    _class_name = "Tax_RecoverabilityObject"
    workday_id: str
    workday_id_type: Literal[
        "Tax_Recoverability_Object_ID"
    ] = "Tax_Recoverability_Object_ID"


class TaxRateOptionsData(BaseModel):

    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Tax_Rate_Options_DataType  # noqa

    With some (in)sane defaults
    """

    tax_rate: TaxRate
    tax_recoverability: TaxRecoverability = TaxRecoverability(
        workday_id="Fully_Recoverable"
    )
    tax_option: TaxOption = TaxOption(workday_id="CALC_TAX_DUE")


class FinancialAttachmentData(File):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Financials_Attachment_DataType  # noqa
    """

    field_type: str = "Financials_Attachment_DataType"


class PrepaidAmortizationType(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Prepaid_Amortization_TypeObjectType  # noqa
    """

    class WorkdayID(str, Enum):
        manual = "Manual"
        schedule = "Schedule"

    _class_name = "Prepaid_Amortization_TypeObject"
    workday_id: WorkdayID
    workday_id_type: Literal[
        "Prepayment_Release_Type_ID"
    ] = "Prepayment_Release_Type_ID"


class AdditionalReferenceType(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v41.1/Submit_Supplier_Invoice.html#Additional_Reference_TypeObjectType  # noqa
    """

    _class_name = "Additional_Reference_TypeObject"
    workday_id_type: Literal[
        "Additional_Reference_Type_ID"
    ] = "Additional_Reference_Type_ID"


class InvoiceAdjustmentReason(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice_Adjustment.html#Invoice_Adjustment_ReasonObjectType  # noqa
    """

    _class_name = "Invoice_Adjustment_ReasonObject"
    workday_id_type: Literal["Adjustment_Reason_ID"] = "Adjustment_Reason_ID"


class SupplierInvoiceLine(BaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Supplier_Invoice_Line_Replacement_DataType  # noqa
    """

    order: int | None = None
    quantity: WorkdayCurrency = Decimal(0)
    description: str = "-No description-"
    tax_rate_options_data: TaxRateOptionsData | None = None
    tax_applicability: TaxApplicability | None = None
    tax_code: TaxCode | None = None
    spend_category: SpendCategory | None = None
    cost_center: CostCenterWorktag | None = None
    project: ProjectWorktag | None = None
    # Incl. VAT
    gross_amount: WorkdayCurrency
    # Excl. VAT
    net_amount: WorkdayCurrency | None = None
    tax_amount: WorkdayCurrency | None = None
    budget_date: date | None = None


class BaseSupplierInvoice(WorkdayReferenceBaseModel):
    """
    Used as base class for SupplierInvoice and SupplierInvoiceAdjustment

    Main reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Supplier_Invoice_DataType  # noqa
    """

    invoice_number: str | None = None
    company: Company
    currency: Currency
    supplier: Supplier
    due_date: WorkdayDate
    total_amount: WorkdayCurrencyHighAccuracy
    tax_amount: WorkdayCurrencyHighAccuracy
    tax_option: TaxOption | None = None
    additional_reference_number: str | None = None
    additional_type_reference: AdditionalReferenceType | None = None
    external_po_number: str | None = None
    prepayment_release_type_reference: PrepaidAmortizationType | None = None

    lines: list[SupplierInvoiceLine]
    attachments: list[FinancialAttachmentData] | None = None

    # Submit to business process rather than uploading invoice in draft mode
    submit: bool = True
    # Should not be edited inside Workday, only through API
    locked_in_workday: bool = True


class SupplierInvoice(BaseSupplierInvoice):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Supplier_Invoice_DataType  # noqa
    """

    workday_id_type: Literal[
        "Supplier_Invoice_Reference_ID"
    ] = "Supplier_Invoice_Reference_ID"

    invoice_date: WorkdayDate
    prepaid: bool = False


class SupplierInvoiceAdjustment(BaseSupplierInvoice):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice_Adjustment.html#Supplier_Invoice_Adjustment_DataType  # noqa
    """

    workday_id_type: Literal[
        "Supplier_Invoice_Adjustment_Reference_ID"
    ] = "Supplier_Invoice_Adjustment_Reference_ID"

    adjustment_date: WorkdayDate
    adjustment_reason: InvoiceAdjustmentReason = InvoiceAdjustmentReason(
        workday_id="Other_Terms"
    )

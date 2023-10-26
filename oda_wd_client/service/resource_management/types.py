from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, validator

from oda_wd_client.base.types import File, WorkdayReferenceBaseModel
from oda_wd_client.base.utils import parse_workday_date
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
    reference_id: str | None
    name: str | None
    payment_terms: str | None
    address: str | None
    phone: str | None
    email: str | None
    url: str | None
    currency: str | None
    bank_account: str | None
    iban: str | None
    primary_transaction_tax_id: str | None


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

    field_type = "Financials_Attachment_DataType"


class PrepaidAmortizationType(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Prepaid_Amortization_TypeObjectType  # noqa
    """

    class WorkdayID(str, Enum):
        manual = "Manual"
        scheduled = "Scheduled"

    _class_name = "Prepaid_Amortization_TypeObject"
    workday_id: WorkdayID
    workday_id_type: Literal[
        "Prepayment_Release_Type_ID"
    ] = "Prepayment_Release_Type_ID"


class SupplierInvoiceLine(BaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Supplier_Invoice_Line_Replacement_DataType  # noqa
    """

    order: int | None
    description: str = "-No description-"
    tax_rate_options_data: TaxRateOptionsData | None
    tax_applicability: TaxApplicability | None
    tax_code: TaxCode | None
    spend_category: SpendCategory | None
    cost_center: CostCenterWorktag | None
    project: ProjectWorktag | None
    # Incl. VAT
    gross_amount: Decimal = Field(max_digits=18, decimal_places=3)
    # Excl. VAT
    net_amount: Decimal | None = Field(max_digits=18, decimal_places=3)
    tax_amount: Decimal | None = Field(max_digits=18, decimal_places=3)
    budget_date: date | None


class SupplierInvoice(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Supplier_Invoice_DataType  # noqa
    """

    workday_id_type: Literal[
        "Supplier_invoice_Reference_ID"
    ] = "Supplier_invoice_Reference_ID"
    invoice_number: str
    company: Company
    currency: Currency
    supplier: Supplier
    invoice_date: date
    due_date: date
    total_amount: Decimal = Field(max_digits=26, decimal_places=6)
    tax_amount: Decimal = Field(max_digits=26, decimal_places=6)
    tax_option: TaxOption | None
    additional_reference_number: str | None
    prepaid: bool = False
    prepayment_release_type_reference: PrepaidAmortizationType | None = None

    lines: list[SupplierInvoiceLine]
    attachments: list[FinancialAttachmentData] | None

    _normalize_dates = validator("invoice_date", "due_date", allow_reuse=True)(
        parse_workday_date
    )

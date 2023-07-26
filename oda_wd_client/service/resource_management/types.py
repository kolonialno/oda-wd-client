from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, validator

from oda_wd_client.base.types import WorkdayReferenceBaseModel
from oda_wd_client.base.utils import parse_workday_date
from oda_wd_client.service.financial_management.types import Company, Currency


class TaxApplicability(WorkdayReferenceBaseModel):
    _class_name = "Tax_ApplicabilityObject"
    workday_id: str
    workday_id_type: Literal["Tax_Applicability_ID"] = "Tax_Applicability_ID"
    # Code is human-readable text but not critical, so we default to empty string
    code: str = ""
    taxable: bool = True


class TaxOption(WorkdayReferenceBaseModel):
    _class_name = "Tax_OptionObject"
    workday_id: str
    workday_id_type: Literal["Tax_Option_ID"] = "Tax_Option_ID"


class TaxCode(WorkdayReferenceBaseModel):
    _class_name = "Tax_CodeObject"
    workday_id: str
    workday_id_type: Literal["Tax_Code_ID"] = "Tax_Code_ID"


class Supplier(WorkdayReferenceBaseModel):
    _class_name = "SupplierObject"
    workday_id: str
    workday_id_type: Literal["Supplier_ID"] = "Supplier_ID"
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

    # Tax ID format and type varies by country. This is organization number in Norway.
    # Norway - VAT
    tax_id_no: str | None
    # Austria - UID
    tax_id_au: str | None
    # Belgium - NOTVA
    tax_id_be: str | None
    # Germany - USTIDNR
    tax_id_de: str | None
    # Denmark - MOMS
    tax_id_dk: str | None
    # Spain - IVA
    tax_id_es: str | None
    # Finland - ALV
    tax_id_fi: str | None
    # Great Britain - VATREGNO
    tax_id_gb: str | None
    # Ireland - VATNO (I think -- it's called "IRE-VATNO" in WD, but IRE is not a valid countrycode)
    tax_id_ir: str | None
    # Netherlands - BTWNR
    tax_id_nl: str | None
    # Sweden - MOMSNR
    tax_id_se: str | None
    # USA - EIN
    tax_id_us: str | None


class TaxRate(WorkdayReferenceBaseModel):
    _class_name = "Tax_RateObject"
    workday_id_type: Literal["Tax_Rate_ID"] = "Tax_Rate_ID"


class TaxRecoverability(WorkdayReferenceBaseModel):
    _class_name = "Tax_RecoverabilityObject"
    workday_id_type: Literal[
        "Tax_Recoverability_Object_ID"
    ] = "Tax_Recoverability_Object_ID"


class SpendCategory(WorkdayReferenceBaseModel):
    _class_name = "Spend_CategoryObject"
    workday_id_type: Literal["Spend_Category_ID"] = "Spend_Category_ID"


class TaxRateOptionsData(BaseModel):
    tax_rate: TaxRate
    tax_recoverability: TaxRecoverability = TaxRecoverability(
        workday_id="Fully_Recoverable"
    )
    tax_option: TaxOption = TaxOption(workday_id="CALC_TAX_DUE")


class CostCenter(WorkdayReferenceBaseModel):
    _class_name = "Accounting_WorktagObject"
    workday_id_type: Literal["Cost_Center_Reference_ID"] = "Cost_Center_Reference_ID"


class SupplierInvoiceLine(BaseModel):
    order: int | None
    description: str | None
    tax_rate_options_data: TaxRateOptionsData
    tax_applicability: TaxApplicability
    tax_code: TaxCode
    spend_category: SpendCategory
    cost_center: CostCenter
    amount: Decimal = Field(max_digits=18, decimal_places=3)


class SupplierInvoice(BaseModel):
    invoice_number: str
    company: Company
    currency: Currency
    supplier: Supplier
    invoice_date: date
    due_date: date
    total_amount: Decimal = Field(max_digits=26, decimal_places=6)
    tax_amount: Decimal = Field(max_digits=26, decimal_places=6)
    tax_option: TaxOption

    lines: list[SupplierInvoiceLine]

    _normalize_dates = validator("invoice_date", "due_date", allow_reuse=True)(
        parse_workday_date
    )

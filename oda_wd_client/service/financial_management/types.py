from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from oda_wd_client.base.types import WorkdayReferenceBaseModel

# All public imports should be done through oda_wd_client.types.financial_management
__all__: list = []


class ConversionRate(BaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Put_Currency_Conversion_Rate.html#Currency_Conversion_Rate_DataType  # noqa
    """

    class RateTypeID(str, Enum):
        # Text reference to Conversion_Rate_Type in Workday
        current = "Current"
        merit = "Merit"
        budget = "Budget"
        average = "Average"

    workday_id: str | None
    # ISO 4217 defines three letters for currency ID
    from_currency_iso: str = Field(max_length=3)
    to_currency_iso: str = Field(max_length=3)

    rate: float
    rate_type_id: RateTypeID = RateTypeID.current
    effective_timestamp: datetime


class ConversionRateType(BaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Put_Currency_Conversion_Rate.html#Currency_Rate_TypeObjectType  # noqa
    """

    workday_id: str
    text_id: str | None
    description: str
    is_default: bool = False


class Currency(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/GetAll_Currencies.html#Currency_DataType  # noqa
    """

    _class_name = "CurrencyObject"
    workday_id: str = Field(max_length=3, alias="currency_code")
    workday_id_type: Literal["Currency_ID"] = "Currency_ID"
    description: str | None = None
    retired: bool = False


class Company(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Get_Workday_Companies.html#Company_WWS_DataType  # noqa
    """

    _class_name = "CompanyObject"
    workday_id: str
    workday_id_type: Literal["Company_Reference_ID"] = "Company_Reference_ID"
    name: str | None
    currency: Currency | None
    country_code: str | None = Field(max_length=2)


class JournalSource(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Submit_Accounting_Journal.html#Journal_SourceObjectType  # noqa
    """

    workday_id: str

    class JournalSourceID(str, Enum):
        # TODO: Get a new value added to workday ("Snowflake_Integration"") (Linear: DIP-1175)
        spreadsheet_upload = "Spreadsheet_Upload"

    _class_name = "Journal_SourceObject"
    workday_id_type: Literal["Journal_Source_ID"] = "Journal_Source_ID"


class LedgerType(WorkdayReferenceBaseModel):
    """
    Holds the type of ledger that we want to submit the journal to - enum values are from Workday.

    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Submit_Accounting_Journal.html#Ledger_TypeObjectType  # noqa
    """

    workday_id: str

    class LedgerTypeID(str, Enum):
        actuals = "Actuals"
        historic_actuals = "Historic_Actuals"

    _class_name = "Ledger_TypeObject"
    workday_id_type: Literal["Ledger_Type_ID"] = "Ledger_Type_ID"


class SpendCategory(WorkdayReferenceBaseModel):
    """
    Worktag? Seems to be dedicated field under Resource_Management at least

    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v40.2/Submit_Supplier_Invoice.html#Spend_CategoryObjectType  # noqa
    """

    _class_name = "Spend_CategoryObject"
    workday_id: str
    workday_id_type: Literal["Spend_Category_ID"] = "Spend_Category_ID"
    name: str | None
    inactive: bool = False


class CostCenterWorktag(WorkdayReferenceBaseModel):
    """
    Reference object used as worktag in accounting. Only holds data needed for use as reference, ant not secondary
    data for cost center objects in Workday.

    Reference:  https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Submit_Accounting_Journal.html#Audited_Accounting_WorktagObjectType  # noqa
    """

    _class_name = "Accounting_WorktagObject"
    workday_id: str
    workday_id_type: Literal["Cost_Center_Reference_ID"] = "Cost_Center_Reference_ID"
    name: str | None


class ProjectWorktag(WorkdayReferenceBaseModel):
    """
    Reference object used as worktag in accounting. Only holds data needed for use as reference, ant not secondary
    data for cost center objects in Workday.

    Reference:  https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Submit_Accounting_Journal.html#Audited_Accounting_WorktagObjectType  # noqa
    """

    _class_name = "Accounting_WorktagObject"
    workday_id: str
    workday_id_type: Literal["Project_ID"] = "Project_ID"
    name: str | None
    inactive: bool = False


class LedgerAccount(WorkdayReferenceBaseModel):
    """
    Reference to a ledger account in Workday.

    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Submit_Accounting_Journal.html#Ledger_AccountObjectType  # noqa
    """

    _class_name = "Ledger_AccountObject"
    workday_id: str
    workday_id_type: Literal["Ledger_Account_ID"] = "Ledger_Account_ID"
    workday_parent_id: str
    workday_parent_type: Literal["Account_Set_ID"] = "Account_Set_ID"


class JournalEntryLineData(BaseModel):
    """
    Represents a single line in a journal entry,
    with enough information to create a journal entry in Workday.

    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Submit_Accounting_Journal.html#Journal_Entry_Line_DataType  # noqa
    """

    ledger_account: LedgerAccount
    debit: Decimal | None = None
    credit: Decimal | None = None
    cost_center: CostCenterWorktag | None = None
    spend_category: SpendCategory | None = None


class AccountingJournalData(BaseModel):
    """
    An accounting journal to be submitted to Workday.
    It's valid for a single company.

    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Financial_Management/v40.2/Submit_Accounting_Journal.html#Accounting_Journal_DataType  # noqa
    """

    accounting_date: date
    company: Company
    ledger_type: LedgerType
    journal_source: JournalSource
    journal_entry_line_data: list[JournalEntryLineData]

    @property
    def accounting_journal_id(self):
        return f"{self.accounting_date.strftime('%Y%m%d')}-{self.company.workday_id}"

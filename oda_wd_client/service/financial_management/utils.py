from suds import sudsobject

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.utils import get_id_from_list
from oda_wd_client.service.financial_management.types import (
    AccountingJournalData,
    Company,
    ConversionRate,
    ConversionRateType,
    CostCenterWorktag,
    Currency,
    JournalEntryLineData,
    ProjectWorktag,
    SpendCategory,
)
from oda_wd_client.service.resource_management.types import TaxApplicability


def workday_conversion_rate_to_pydantic(data: dict) -> ConversionRate:
    """
    Create a ConversionRate pydantic object from a suds datadict from Workday
    """
    workday_id = get_id_from_list(
        data["Currency_Conversion_Rate_Reference"]["ID"], "WID"
    )
    assert len(data["Currency_Conversion_Rate_Data"]) == 1, (
        "Code is written expecting that we only have one currency "
        "rate data per object, but that is not the case here"
    )
    sub_data = data["Currency_Conversion_Rate_Data"][0]
    from_ref = get_id_from_list(
        sub_data["From_Currency_Reference"]["ID"], "Currency_ID"
    )
    target_ref = get_id_from_list(
        sub_data["Target_Currency_Reference"]["ID"], "Currency_ID"
    )
    type_id = get_id_from_list(
        sub_data["Currency_Rate_Type_Reference"]["ID"], "Currency_Rate_Type_ID"
    )

    assert workday_id, "All currency conversion rates need a Workday ID"
    assert from_ref, "All currency conversion rates need a 'from currency'-reference"
    assert (
        target_ref
    ), "All currency conversion rates need a 'target currency'-reference"
    assert type_id, "All currency conversion rates need a 'rate type'-reference"

    return ConversionRate(
        workday_id=workday_id,
        from_currency_iso=from_ref,
        to_currency_iso=target_ref,
        rate=sub_data["Currency_Rate"],
        rate_type_id=ConversionRate.RateTypeID(type_id),
        effective_timestamp=sub_data["Effective_Timestamp"],
    )


def workday_conversion_rate_type_to_pydantic(data: dict) -> ConversionRateType:
    """
    Create a ConversionRateType pydantic object from a suds datadict from Workday
    """
    workday_id = get_id_from_list(data["Currency_Rate_Type_Reference"]["ID"], "WID")
    assert workday_id, "All currency conversion rate types need a Workday ID"
    assert len(data["Currency_Rate_Type_Data"]) == 1, (
        "Code is written to expect that we only have one currency "
        "rate type data per object, but that is not the case here"
    )
    sub_data = data["Currency_Rate_Type_Data"][0]
    return ConversionRateType(
        workday_id=workday_id,
        text_id=sub_data["Currency_Rate_Type_ID"],
        description=sub_data["Currency_Rate_Type_Description"],
        is_default=sub_data["Currency_Rate_Type_Default"],
    )


def workday_company_to_pydantic(data: dict) -> Company:
    # For some weird reason, the object that holds the data for a specific company is wrapped in a list
    assert (
        len(data["Company_Data"]) == 1
    ), "Company_Data for each company should be singular"
    cdata = data["Company_Data"][0]

    currency_code = get_id_from_list(
        cdata["Accounting_Data"]["Currency_Reference"]["ID"], "Currency_ID"
    )
    # We'll expect that each company only has to care about taxation in one jurisdiction, and use the first object
    if "Tax_Status_Data" in cdata:
        country_code = get_id_from_list(
            cdata["Tax_Status_Data"][0]["Country_Reference"]["ID"],
            "ISO_3166-1_Alpha-2_Code",
        )
    else:
        country_code = None

    return Company(
        workday_id=cdata["Organization_Data"]["ID"],
        name=cdata["Organization_Data"]["Organization_Name"],
        country_code=country_code,
        currency=Currency(currency_code=currency_code) if currency_code else None,
    )


def workday_currency_to_pydantic(data: dict) -> Currency:
    return Currency(
        currency_code=data["Currency_ID"],
        description=data["Currency_Description"],
        retired=data["Currency_Retired"],
    )


def workday_tax_applicability_to_pydantic(data: dict) -> TaxApplicability:
    data = data["Tax_Applicability_Data"]
    return TaxApplicability(
        workday_id=data["Tax_Applicability_ID"],
        code=data["Tax_Applicability_Code"],
        taxable=data["Taxable"],
    )


def workday_cost_center_to_pydantic(data: dict) -> CostCenterWorktag:
    cost_center_id = get_id_from_list(
        data["Cost_Center_Reference"]["ID"], "Cost_Center_Reference_ID"
    )
    assert cost_center_id, "No ID of cost center found, this is required"
    return CostCenterWorktag(
        workday_id=cost_center_id,
        name=data["Cost_Center_Data"]["Organization_Data"]["Organization_Name"],
    )


def workday_spend_category_to_pydantic(data: dict) -> SpendCategory:
    cat_data = data["Resource_Category_Data"]
    ref_id = get_id_from_list(
        data["Resource_Category_Reference"]["ID"], "Spend_Category_ID"
    )
    resource_id = cat_data["Resource_Category_ID"]
    assert (
        ref_id == resource_id
    ), "The Resource_Category_ID and Spend_Category_ID are expected to be equal"

    return SpendCategory(
        workday_id=ref_id,
        name=cat_data["Resource_Category_Name"],
        inactive=cat_data["Inactive"],
    )


def workday_project_to_pydantic(data: dict) -> ProjectWorktag:
    proj_data = data["Basic_Project_Data"]
    return ProjectWorktag(
        workday_id=proj_data["Project_ID"],
        name=proj_data["Project_Name"],
        inactive=proj_data["Inactive"],
    )


def pydantic_conversion_rate_to_workday(
    rate: ConversionRate, client: WorkdayClient
) -> sudsobject.Object:
    """
    Create a suds object from a Pydantic object. Used for creating/updating conversion rates in Workday
    """
    rate_data = client.factory("ns0:Currency_Conversion_Rate_DataType")
    from_currency_id = client.factory("ns0:CurrencyObjectIDType")
    target_currency_id = client.factory("ns0:CurrencyObjectIDType")
    rate_type_id = client.factory("ns0:Currency_Rate_TypeObjectIDType")

    # Populate objects
    rate_data.Effective_Timestamp = rate.effective_timestamp
    rate_data.Currency_Rate = rate.rate
    from_currency_id.value = rate.from_currency_iso
    target_currency_id.value = rate.to_currency_iso
    rate_data.Calculate_Inverse_Rate = True

    # Stuff everything into the final object
    from_currency_id._type = "Currency_ID"
    target_currency_id._type = "Currency_ID"
    from_currency = client.factory("ns0:CurrencyObjectType")
    target_currency = client.factory("ns0:CurrencyObjectType")
    from_currency.ID.append(from_currency_id)
    target_currency.ID.append(target_currency_id)
    rate_type_id._type = "Currency_Rate_Type_ID"
    rate_type_id.value = rate.rate_type_id.value
    rate_type = client.factory("ns0:Currency_Rate_TypeObjectType")
    rate_type.ID.append(rate_type_id)
    rate_data.From_Currency_Reference = from_currency
    rate_data.Target_Currency_Reference = target_currency
    rate_data.Currency_Rate_Type_Reference = rate_type

    return rate_data


def _pydantic_journal_entry_line_to_workday(
    journal_line: JournalEntryLineData, client: WorkdayClient
) -> sudsobject.Object:
    wd_journal_entry_line = client.factory("ns0:Journal_Entry_Line_DataType")

    wd_journal_entry_line.Ledger_Account_Reference = (
        journal_line.ledger_account.wd_object(client)
    )

    if journal_line.spend_category:
        spend_category = journal_line.spend_category.wd_object(client)
        wd_journal_entry_line.Worktags_Reference.append(spend_category)

    if journal_line.cost_center:
        cost_center = journal_line.cost_center.wd_object(client)
        wd_journal_entry_line.Worktags_Reference.append(cost_center)

    wd_journal_entry_line.Debit_Amount = journal_line.debit
    wd_journal_entry_line.Credit_Amount = journal_line.credit

    return wd_journal_entry_line


def pydantic_accounting_journal_to_workday(
    journal: AccountingJournalData, client: WorkdayClient
) -> sudsobject.Object:
    """
    Create a suds object from a Pydantic object. Used for submitting accounting journals to Workday
    """
    # create container object and add data
    wd_accounting_journal = client.factory("ns0:Accounting_Journal_DataType")
    wd_accounting_journal.Accounting_Date = journal.accounting_date
    wd_accounting_journal.Accounting_Journal_ID = journal.accounting_journal_id
    wd_accounting_journal.Journal_Source_Reference = journal.journal_source.wd_object(
        client
    )
    if journal.company.currency:
        wd_accounting_journal.Currency_Reference = journal.company.currency.wd_object(
            client
        )
    wd_accounting_journal.Company_Reference = journal.company.wd_object(client)
    wd_accounting_journal.Ledger_Type_Reference = journal.ledger_type.wd_object(client)
    for journal_entry_line_data in journal.journal_entry_line_data:
        wd_data = _pydantic_journal_entry_line_to_workday(
            journal_entry_line_data, client
        )
        wd_accounting_journal.Journal_Entry_Line_Replacement_Data.append(wd_data)

    return wd_accounting_journal

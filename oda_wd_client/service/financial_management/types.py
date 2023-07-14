from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import Field, BaseModel

from oda_wd_client.base.types import WorkdayReferenceBaseModel


class ConversionRate(BaseModel):
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
    workday_id: str
    text_id: str | None
    description: str
    is_default: bool = False


class Currency(WorkdayReferenceBaseModel):
    workday_id: str = Field(max_length=3, alias='currency_code')
    workday_id_type: Literal['Currency_ID'] = 'Currency_ID'
    currency_code: str
    description: str | None
    retired: bool = False


class Company(WorkdayReferenceBaseModel):
    workday_id: str
    workday_id_type: Literal['Company_Reference_ID'] = 'Company_Reference_ID'
    name: str
    currency: Currency
    country_code: str | None = Field(max_length=2)

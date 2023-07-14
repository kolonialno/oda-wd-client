from typing import Iterator

from suds import sudsobject

from oda_wd_client.base.tools import suds_to_dict
from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.service.financial_management.utils import (
    workday_conversion_rate_to_pydantic, workday_conversion_rate_type_to_pydantic, workday_company_to_pydantic,
    workday_currency_to_pydantic, workday_tax_applicability_to_pydantic, pydantic_conversion_rate_to_workday
)
from oda_wd_client.service.financial_management.types import ConversionRate, ConversionRateType, Company, Currency


class FinancialManagement(WorkdayClient):
    service = "Financial_Management"

    def get_currency_rates(self, return_suds_object=False) -> Iterator[sudsobject.Object | ConversionRate]:
        method = "Get_Currency_Conversion_Rates"
        results = self._get_paginated(method, "Currency_Conversion_Rate")
        for rate in results:
            yield rate if return_suds_object else workday_conversion_rate_to_pydantic(suds_to_dict(rate))

    def get_currency_rate_types(self, return_suds_object=False) -> Iterator[sudsobject.Object | ConversionRateType]:
        method = "Get_Currency_Rate_Types"
        results = self._get_paginated(method, "Currency_Rate_Type")
        for rate_type in results:
            yield rate_type if return_suds_object else workday_conversion_rate_type_to_pydantic(suds_to_dict(rate_type))

    def put_currency_rate(self, rate: ConversionRate) -> sudsobject.Object:
        data_object = pydantic_conversion_rate_to_workday(rate, client=self)
        return self._request("Put_Currency_Conversion_Rate", Currency_Conversion_Rate_Data=data_object)

    def get_cost_centers(self, return_suds_object=False) -> Iterator[sudsobject.Object | ConversionRateType]:
        method = "Get_Cost_Centers"
        results = self._get_paginated(method, "Cost_Center")
        for cost_center in results:
            yield cost_center if return_suds_object else suds_to_dict(cost_center)

    def get_companies(self, return_suds_object=False) -> Iterator[sudsobject.Object | Company]:
        method = "Get_Workday_Companies"
        results = self._get_paginated(method, "Company")
        for company in results:
            yield company if return_suds_object else workday_company_to_pydantic(suds_to_dict(company))

    def get_currencies(self, return_suds_object=False) -> Iterator[sudsobject.Object | Currency]:
        method = "GetAll_Currencies"
        response = self._request(method)
        results = response.Currency_Data
        for currency in results:
            yield currency if return_suds_object else workday_currency_to_pydantic(suds_to_dict(currency))

    def get_tax_applicabilities(self, return_suds_object: bool = False) -> Iterator[sudsobject.Object | dict]:
        method = "Get_Tax_Applicabilities"
        results = self._get_paginated(method, "Tax_Applicability")
        for tax_applicability in results:
            if return_suds_object:
                yield tax_applicability
            else:
                yield workday_tax_applicability_to_pydantic(suds_to_dict(tax_applicability))

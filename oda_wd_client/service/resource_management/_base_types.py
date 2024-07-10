"""
Some models are used both inside `resource_management` as well as other scopes. To avoid circular imports,
we put these in _base_types.py to allow them to be imported from inside other services.
"""
from typing import Literal

from oda_wd_client.base.types import WorkdayReferenceBaseModel


class Organization(WorkdayReferenceBaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Resource_Management/v42.1/Get_Suppliers.html#OrganizationObjectType  # noqa
    """

    _class_name = "OrganizationObject"
    workday_id: str
    workday_id_type: Literal["Organization_Reference_ID"] = "Organization_Reference_ID"

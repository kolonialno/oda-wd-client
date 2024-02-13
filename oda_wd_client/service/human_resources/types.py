from pydantic import BaseModel

# All public imports should be done through oda_wd_client.types.human_resources
__all__: list = []


class Worker(BaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Human_Resources/v40.2/Get_Workers.html#Worker_DataType   # noqa
    """

    workday_id: str
    employee_number: str | None = None
    name: str
    work_email: str | None = None
    secondary_email: str | None = None


class PersonReference(BaseModel):
    """
    This is kind of hacky, but allows us to represent a "Role" with a single ref ID, as well as Workday ID. It
    corresponds to the RoleObject in the HumanResources section of the API, but the fields are not 1-to-1 with their
    Workday counterparts.

    When we get this data from Workday, we -usually- get a list of two IDs -- one with WID (Workday ID), and one with a
    more arbitrary name (like "Employee_ID" or "Contingent_Worker_ID"). This class exists to collect and represent a
    subset of this data, and is not really expandable to support all uses of "RoleType" in Workday.
    """

    workday_id: str | None = None
    ref_type: str
    ref_id: str


class UniversalId(BaseModel):
    """
    As with PersonReference, this model does not reflect a Workday type 1-to-1, but rather serves as a simplified way
    to hold and represent the data we need when dealing with the Universal ID endpoints.

    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Human_Resources/v41.2/Put_Universal_Identifier.html#RoleObjectType  # noqa
    """

    id: str
    person_reference: PersonReference
    other_references: list[PersonReference]

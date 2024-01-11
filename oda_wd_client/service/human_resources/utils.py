from typing import Optional, Tuple

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.service.human_resources.types import (
    PersonReference,
    UniversalId,
    Worker,
)

WORKDAY_EMAIL_TYPES = {"WORK": "work", "HOME": "secondary"}


def _parse_worker_emails(emails: list) -> dict[str, str]:
    """
    E-mail addresses in Workday are nested deep, and we want to only extract primary addresses
    """
    ret = {}

    def _parse_address(data) -> Tuple[Optional[str], str]:
        usage_type_id = None
        addr = email["Email_Address"]
        for ud in email["Usage_Data"]:
            for td in ud["Type_Data"]:
                # Only use address if it's primary
                is_primary = td["_Primary"]
                # Lookup usage type ID - denotes if the address is work or personal
                usage_type_id = [
                    d["value"]
                    for d in td["Type_Reference"]["ID"]
                    if d["_type"] == "Communication_Usage_Type_ID"
                ]
                if is_primary and usage_type_id:
                    return usage_type_id[0], addr
        return None, ""

    for email in emails:
        wd_usage_type, _addr = _parse_address(email)
        if not wd_usage_type:
            continue
        _type = WORKDAY_EMAIL_TYPES[wd_usage_type]
        ret[_type] = _addr

    return ret


def _parse_worker_refs(
    refs: dict, employee_number_field: str = "Employee_ID"
) -> Tuple[Optional[str], Optional[str]]:
    workday_id = None
    employee_number = None
    for ref in refs:
        _type = ref["_type"]
        value = ref["value"]
        if _type == "WID":
            workday_id = value
        elif _type == employee_number_field:
            employee_number = value
    return workday_id, employee_number


def workday_worker_to_pydantic(
    data: dict, employee_number_field: str = "Employee_ID"
) -> Worker:
    """
    Workday objects are painful and complex creatures, and we want to normalize them to something
    which is much easier for us to use in Python.
    """
    # Alias
    worker_data = data["Worker_Data"]
    refs = data["Worker_Reference"]["ID"]
    personal_data = worker_data["Personal_Data"]
    name_data = personal_data["Name_Data"]
    emails_data = personal_data["Contact_Data"].get("Email_Address_Data", [])

    # Lookup
    name = name_data["Legal_Name_Data"]["Name_Detail_Data"]["_Formatted_Name"]

    # Parsing
    workday_id, employee_number = _parse_worker_refs(
        refs, employee_number_field=employee_number_field
    )
    assert (
        workday_id
    ), "We require Workday ID for worker objects. Something is very wrong if we cannot look that up."
    emails = _parse_worker_emails(emails_data)

    return Worker(
        workday_id=workday_id,
        employee_number=employee_number,
        name=name,
        work_email=emails.get("work", None),
        secondary_email=emails.get("secondary", None),
    )


def _workday_person_reference_to_pydantic(data: list) -> PersonReference:
    """
    Interprets a list of ref IDs for a RoleObject for the Universal ID endpoints

    Naively expects each list to have exactly two ID items; one with WID and one with an arbitrary ID.

    :param data: List of ref IDs ("RoleObjectID")
    :return: Pydantic PersonReference
    """
    ids = {d["_type"]: d["value"] for d in data}
    wid = ids.pop("WID")
    if not len(ids) == 1:
        raise Exception(
            "The person reference should only have two IDs -- WID plus another one"
        )
    _type, _value = ids.popitem()
    return PersonReference(workday_id=wid, ref_type=_type, ref_id=_value)


def workday_universal_id_to_pydantic(data: dict) -> UniversalId:
    """
    Parse a Workday Universal ID object from the SOAP endpoint

    :param data: Dict representation of the data from Workday for one instance of Universal ID
    :return: An interpreted pydantic UniversalId
    """
    person_ref = _workday_person_reference_to_pydantic(data["Person_Reference"]["ID"])
    other_refs = []

    if len(data["Universal_Identifier_Data"]) > 1:
        raise Exception("We should only have one universal identifier data item")

    uidata = data["Universal_Identifier_Data"][0]
    for ref in uidata["Person_Reference"]:
        other_refs.append(_workday_person_reference_to_pydantic(ref["ID"]))

    return UniversalId(
        id=uidata["Universal_ID"],
        person_reference=person_ref,
        other_references=other_refs,
    )


def pydantic_universal_id_to_request_params(
    client: WorkdayClient, obj: UniversalId
) -> dict:
    """
    Generate the parameters for a request to set the Universal Identifier in Workday

    The Universal Identifier structure in Workday is a bit finicky, and looks something like this,
        * The ID itself (unique within the scope of "Universal ID")
        * A reference that leads to a person (i.e. a Worker, Contingent Worker, Applicant etc.)
        * List of all references that the universal identifier covers

    This method takes a UniversalId pydantic object and generates the corresponding Workday SOAP data, so that it can
    be expanded directly into an API call to the Workday web service.

    Our usual pattern employs the WorkdayReferenceBaseModel, but we need this implementation to be a bit more abstract,
    and support multiple ID types, so we just ended up coding all the Workday data population from scratch.

    :param client: WorkdayClient to use for SOAP factory calls
    :param obj: The UniversalId pydantic object
    :return: A dict of parameters needed to call the SOAP API endpoint
    """

    ref_obj = client.factory("ns0:RoleObjectType")
    ref_id = client.factory("ns0:RoleObjectIDType")
    ref_id.value = obj.person_reference.ref_id
    ref_id._type = obj.person_reference.ref_type
    ref_obj.ID.append(ref_id)

    uid_data = client.factory("ns0:Universal_Identifier_DataType")
    for ref in obj.other_references:
        _ref_id = client.factory("ns0:RoleObjectIDType")
        _ref_id.value = ref.ref_id
        _ref_id._type = ref.ref_type
        _ref_obj = client.factory("ns0:RoleObjectType")
        _ref_obj.ID.append(_ref_id)

        uid_data.Person_Reference.append(_ref_obj)
        uid_data.Universal_ID = obj.id

    return {"Person_Reference": ref_obj, "Universal_Identifier_Data": uid_data}

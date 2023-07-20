from typing import Optional, Tuple

from oda_wd_client.service.human_resources.types import Worker

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


def _parse_worker_refs(refs: dict) -> Tuple[Optional[str], Optional[str]]:
    workday_id = None
    employee_number = None
    for ref in refs:
        _type = ref["_type"]
        value = ref["value"]
        if _type == "WID":
            workday_id = value
        elif _type == "Employee_ID":
            employee_number = value
    return workday_id, employee_number


def workday_worker_to_pydantic(data: dict) -> Worker:
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
    workday_id, employee_number = _parse_worker_refs(refs)
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

from datetime import datetime

# As defined by API docs
WORKDAY_DATE_FORMAT = "%m/%d/%Y"


def get_id_from_list(id_list: list, id_type: str) -> str | None:
    """
    Workday operates with a lot of fields that contains list of IDs. We often want to extract a single value of
    these, based on the type of the ID.

    Will return the first ID matching the type (there should only be one), or None if no ID matches the type.

    Args:
        id_list: List of ID dicts (not suds objects) from Workday
        id_type: The value we'll use to filter on _type
    """
    ids = [ref["value"] for ref in id_list if ref["_type"] == id_type]
    if ids:
        return ids[0]
    return None


def parse_workday_date(val):
    if isinstance(val, str):
        return datetime.strptime(val, WORKDAY_DATE_FORMAT).date()
    return val

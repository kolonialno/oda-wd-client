from datetime import date, datetime

# As defined by API docs
WORKDAY_DATE_FORMAT = "%m/%d/%Y"
WORKDAY_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"  # i.e. 2024-02-28T12:34:56Z


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


def parse_workday_date(val: str | date | None) -> date | None:
    if isinstance(val, str):
        return datetime.strptime(val, WORKDAY_DATE_FORMAT).date()
    return val


def localize_datetime_to_string(dt: datetime) -> str:
    """
    Localize and format datetime for Workday

    From the WD docs:
        When you enter or load currency conversion rates, Workday automatically converts the timestamp to the Pacific
        time zone. Workday therefore recommends that you enter the timestamp to adjust for the difference between your
        time and Pacific time. Example: When you enter a conversion rate to be effective at 12.00 am Greenwich Mean
        Time (GMT) which is 8 hours ahead of Pacific time, adjust your timestamp to 8.00 AM Pacific time of the same
        calendar day. The timestamp visible on the Historic Currency Rates report will display as 8.00 AM, however,
        Workday converts it to recognize it as 12.00 AM Pacific time.

        https://doc.workday.com/admin-guide/en-us/manage-workday/tenant-configuration/globalization/currencies/dan1370796986531.html  # noqa

    Testing has shown us that not including the timezone in the timestamp will make the timestamp correct on the
    Workday side. For instance, the datetime 2024-02-04T00:00:00+01:00 is shown as 2024-02-04T00:00:00,
    but effective at 2024-02-03T15:0:00:00. The datetime 2024-02-04T00:00:00, however, will get shown as
    2024-02-04T09:00:00 and is effective from 2024-02-04T00:00:00.

    Since the internal Workday logic run in Pacific time (-08:00), we have to make sure that the effective timestamp
    is midnight, as that is the Pacific time representation. If we were to send in timezone as part of the timestamp,
    we would have to add the difference between Pacific time and the timezone of the input timestamp.

    Just sending the datetime, at midnight, without timezone appears to yield the correct result.

    https://youtu.be/-5wpm-gesOY

    :param dt: Timezone-aware datetime object
    :return: String representation for Workday payload
    """
    return dt.strftime(WORKDAY_DATETIME_FORMAT)

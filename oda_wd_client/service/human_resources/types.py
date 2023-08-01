from typing import Optional

from pydantic import BaseModel

# All public imports should be done through oda_wd_client.types.human_resources
__all__: list = []


class Worker(BaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Human_Resources/v40.2/Get_Workers.html#Worker_DataType   # noqa
    """

    workday_id: str
    employee_number: Optional[str]
    name: str
    work_email: Optional[str]
    secondary_email: Optional[str]

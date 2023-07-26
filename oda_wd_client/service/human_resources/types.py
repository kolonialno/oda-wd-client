from typing import Optional

from pydantic import BaseModel

# All public imports should be done through oda_wd_client.types.human_resources
__all__: list = []


class Worker(BaseModel):
    workday_id: str
    employee_number: Optional[str]
    name: str
    work_email: Optional[str]
    secondary_email: Optional[str]

from typing import Optional

from pydantic import BaseModel


class Worker(BaseModel):
    workday_id: str
    employee_number: Optional[str]
    name: str
    work_email: Optional[str]
    secondary_email: Optional[str]

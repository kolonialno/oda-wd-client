from base64 import b64encode
from typing import Self

import magic
from pydantic import BaseModel
from suds import sudsobject

from oda_wd_client.base.api import WorkdayClient
from oda_wd_client.base.utils import get_id_from_list

mime = magic.Magic(mime=True)


class WorkdayReferenceBaseModel(BaseModel):
    """
    Base class for all Workday reference models.
    A reference model is a model that is used to reference another pre-existing object in Workday.
    These models are used to have a simple/convenient way to generate reference objects for Workday, through the use of
    workday_id and workday_id_type.
    """

    workday_id: str | None
    workday_id_type: str
    workday_parent_id: str | None = None
    workday_parent_type: str | None = None

    # This is the name of the class in Workday. Usually ends with "Object" (i.e. "SupplierObject")
    _class_name: str | None = None

    def wd_object(
        self,
        client: WorkdayClient,
        class_name: str | None = None,
    ) -> sudsobject.Object:
        class_name = class_name or self._class_name
        assert (
            class_name
        ), "WD Class name must be supplied on class or call to wd_object"

        ref_obj = client.factory(f"ns0:{class_name}Type")
        id_obj = client.factory(f"ns0:{class_name}IDType")
        id_obj.value = self.workday_id
        id_obj._type = self.workday_id_type
        if self.workday_parent_id:
            id_obj._parent_id = self.workday_parent_id
            id_obj._parent_type = self.workday_parent_type

        ref_obj.ID.append(id_obj)
        return ref_obj

    @classmethod
    def from_id_list(cls, id_list: list, **extra) -> Self | None:
        """
        Make an instance of Self based on an ID list, using self.workday_id_type to look up the specified Workday ID

        The ID lists used for references are usually in the following format:

        id_list = {
            "Field_Reference": {
                "ID": [
                    {"_type": "Field_ID", value="ABC"},
                    {"_type": "WID", value="123456789"}
                ]
            }
        }

        `get_id_from_list(id_list, "Field_ID")` would give us "ABC".

        As the "field ID" value is defined on Self, as `workday_id_type`, we can simplify this lookup, and directly
        instantiate an instance based on the class definition and ID list.

        Example use:
            > SpendCategory.from_id_list(data["Spend_Category_Reference"]["ID"])

        :param id_list: List of IDs
        :param extra: Arbitrary kwargs are passed onto `cls.__init__()`
        :return: instance of Self
        """
        workday_id = get_id_from_list(
            id_list, cls.__fields__["workday_id_type"].default
        )
        if workday_id:
            return cls(workday_id=workday_id, **extra)
        return None


class File(BaseModel):
    """
    Representing a file in Workday, complete with MIME-identification and serialization

    Used as part of various fields within the web service
    """

    # All documents need a field type which is unique for each implementation (i.e. "Financials_Attachment_DataType"
    # or "Worker_Document_DataType")
    field_type: str

    filename: str
    file_content: bytes
    comment: str | None
    content_type: str | None

    def wd_object(self, client: WorkdayClient):
        doc = client.factory(f"ns0:{self.field_type}")
        doc.File_Content = b64encode(self.file_content).decode("utf-8")
        doc._Filename = self.filename
        doc._Content_Type = self.content_type or self._get_content_type()
        if self.comment:
            doc.Comment = self.comment
        return doc

    def _get_content_type(self):
        return mime.from_buffer(self.file_content)

from pydantic import BaseModel
from suds import sudsobject


class WorkdayReferenceBaseModel(BaseModel):
    """
    Base class for all Workday reference models.
    A reference model is a model that is used to reference another pre-existing object in Workday.
    These models are used to have a simple/convenient way to generate reference objects for Workday, through the use of
    workday_id and workday_id_type.
    """

    workday_id: str
    workday_id_type: str
    workday_parent_id: str | None = None
    workday_parent_type: str | None = None

    # This is the name of the class in Workday. Usually ends with "Object" (i.e. "SupplierObject")
    _class_name: str | None = None

    def wd_object(
        self,
        client,
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

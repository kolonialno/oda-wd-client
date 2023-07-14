from oda_wd_client.service.staffing.types import Document


def workday_document_to_pydantic(data: dict) -> Document:
    """
    Take a dict from `suds_to_dict` of a single document and generate a Document instance instead
    """
    doc_data = data["Worker_Document_Data"]
    filename = doc_data["Filename"]
    comment = doc_data.get("Comment", "")
    employee_number = [
        field["value"]
        for field in doc_data["Worker_Reference"]["ID"]
        if field["_type"] == "Employee_ID"
    ][0]

    cat_wd = None
    cat_oda = None
    for ref in doc_data["Document_Category_Reference"]["ID"]:
        if ref["_type"] == "Document_Category__Workday_Owned__ID":
            cat_wd = ref["value"]
        elif ref["_type"] == "Document_Category_ID":
            cat_oda = ref["value"]

    return Document(
        employee_number=employee_number,
        wd_owned_category=cat_wd,
        oda_category=cat_oda,
        filename=filename,
        comment=comment,
    )

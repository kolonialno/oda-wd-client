from enum import Enum

from pydantic import BaseModel

# All public imports should be done through oda_wd_client.types.staffing
__all__: list = []


class Document(BaseModel):
    """
    Reference: https://community.workday.com/sites/default/files/file-hosting/productionapi/Staffing/v40.2/Put_Worker_Document.html#Worker_Document_DataType  # noqa
    """

    class WorkdayCategory(str, Enum):
        employee_contract = "EMPLOYEE_CONTRACT"
        student_collections = "STUDENT_COLLECTIONS"
        prospect_resume_cover_letter = "PROSPECT_RESUME_AND_COVER_LETTER"
        candidate_resume_cover_letter = "CANDIDATE_RESUME_AND_COVER_LETTER"
        residency_determination = "RESIDENCY_DETERMINATION"
        education = "EDUCATION"
        multimedia_audio = "MULTI_MEDIA_AUDIO"
        multimedia_video = "MULTI_MEDIA_VIDEO"
        drive_document_template = "DRIVEDOCUMENTTEMPLATE"
        committees = "COMMITTEES"
        recommendation = "RECOMMENDATION"
        position = "POSITION"
        credential = "CREDENTIAL"
        retiree = "RETIREE"
        application = "APPLICATION"
        secondary = "SEC"
        action_item = "ACTION_ITEM"
        reference_letter = "REFERENCE_LETTER"
        accommodation_verification = "ACCOMMODATION_VERIFICATION"
        probation_period = "PROBATION_PERIOD"
        language_proficiency = "LANGUAGE_PROFICIENCY"
        time_off = "TIME_OFF"
        portfolio = "PORTFOLIO"
        resume = "RESUME"
        writing_sample = "WRITING_SAMPLE"
        benefits = "BENEFITS"
        verification = "VERIFICATION"
        certification = "CERT"
        company_policy_related = "COMPANY_POLICY_RELATED"
        leave_of_absence = "LOA"
        personal_information = "PERSONAL_INFORMATION"
        time_tracking = "TIME_TRACKING"
        offers = "OFFERS"
        background_check = "BACKGROUND CHECK"
        assessment = "ASSESSMENT"
        interview = "INTERVIEW"
        other_documents = "OTHER_DOCUMENTS"
        agency = "AGENCY"
        academic_appointments = "ACADEMIC_APPOINTMENTS"
        period_activity_pay = "PERIOD_ACTIVITY_PAY"
        named_professorships = "NAMED_PROFESSORSHIPS"
        notice_period = "NOTICE_PERIOD"
        licenses = "LICENSES"
        passports_and_visas = "PASSPORTS_AND_VISAS"
        dependents = "DEPENDENTS"
        employment_agreement = "EMPLOYMENT_AGREEMENT"
        other_student = "OTHER_STUDENT"
        international_student = "INTERNATIONAL_STUDENT"

    class OdaCategory(str, Enum):
        # TODO: Make this model extendable so that we do not have to hardcode our values here
        tax_forms = "DOC_CAT_Tax_Forms"
        non_disclosure_agreement = "DOC_CAT_Non-Disclosure_Agreement"
        id_verification = "DOC_CAT_ID_Verification"
        other_documents_offboarding = "DOC_CAT_Other_Documents_Offboarding"
        compensation = "DOC_CAT_Compensation"
        transfer = "DOC_CAT_Transfer"
        promotion = "DOC_CAT_Promotion"
        nav_documents = "DOC_CAT_NAV_Documents"
        education_reimbursement = "DOC_CAT_Education_Reimbursement"
        contingent_worker_contract = "DOC_CAT_Contingent_Worker_Contract"
        termination = "DOC_CAT_Termination"
        doctors_notice = "DOC_CAT_Doctors_notice"
        hire = "DOC_CAT_Hire"
        sick_leave = "DOC_CAT_Sick_Leave"
        internal_documents = "DOC_CAT_Internal_documents_(not_visible_for_employee)"
        other_employee_documents = "DOC_CAT_Other_employee_documents"

    employee_number: str
    wd_owned_category: WorkdayCategory | None
    oda_category: OdaCategory | None
    filename: str
    comment: str

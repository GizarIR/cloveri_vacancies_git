import datetime
import enum
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel

from app.core import config


class MessageTypes(str, enum.Enum):
    IDS_DONT_MATCH = "ids_dont_match"
    NOT_FOUND = "not_found"
    VACANCY_DELETED = "deleted"
    INVALID_FILTERS = "invalid_filter"
    SIGNATURE_DONT_MATCH = "invalid_signature"
    SERVICE_UNAVAILABLE = "service_unavailable"
    VACANCY_NOTIFY = "notified"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"


class MessageTexts(str, enum.Enum):
    GP_PROJECT_ID_NOT_FOUND = "ID project group of companies  {} is not found"
    GP_PROJECT_ID_NOT_FOUND_OR_NOT_REGISTRY = (
        "ID project group of companies  {} is not found or Registry service is not available"
    )
    IDS_DONT_MATCH = "Vacancy id in path and in body do not match"
    VACANCY_NOT_FOUND = "Vacancy {} is not found"
    VACANCIES_NOT_FOUND = "No vacancies found for chosen filters"
    VACANCY_RESPONSE_NOT_FOUND = "Vacancy's response {} is not found"
    VACANCY_RESPONSES_NOT_FOUND = "No responses for this vacancy found for chosen filters"
    USER_RESPONSES_NOT_FOUND = "No responses for this user found for chosen filters"
    VACANCY_DELETED = "Vacancy {} is successfully deleted"
    INVALID_FILTERS = (
        "At least one of {company_id, profession_id, team_id} must be specified"
    )
    INVALID_FILTERS_RESPONSE = (
        "{vacancy_id} must be specified"
    )
    INVALID_FILTERS_USER_RESPONSES = (
        "At least one of {gp_user_id, first_name, last_name, middle_name, email, phone} must be specified"
    )
    INVALID_SIGNATURE = "Invalid signature"
    SERVICE_IS_UNAVAILABLE = "Remote service {} is unavailable for some reason "
    VACANCY_NOTIFIED = "Vacancy {} is successfully notified"
    SERVICE_VALIDATION_ERROR = "Remote service {} returned error: {}"
    AUTHENTICATION_TIMEOUT_ERROR = "Timeout signature {}"


class Detail(BaseModel):
    msg: str
    type: str


class Message(BaseModel):
    detail: List[Detail]


class MessageManager:
    @staticmethod
    def make_message(msg: str, _type: str):
        return {"detail": [{"msg": msg, "type": _type}]}

    @staticmethod
    def get_ids_dont_match_msg() -> Dict:
        return MessageManager.make_message(
            MessageTexts.IDS_DONT_MATCH, MessageTypes.IDS_DONT_MATCH
        )

    @staticmethod
    def get_vacancy_not_found_msg(vacancy_id: UUID) -> Dict:
        return MessageManager.make_message(
            MessageTexts.VACANCY_NOT_FOUND.format(vacancy_id), MessageTypes.NOT_FOUND
        )

    @staticmethod
    def get_nothing_found_msg() -> Dict:
        return MessageManager.make_message(
            MessageTexts.VACANCIES_NOT_FOUND, MessageTypes.NOT_FOUND
        )

    @staticmethod
    def get_nothing_responses_found_msg() -> Dict:
        return MessageManager.make_message(
            MessageTexts.VACANCY_RESPONSES_NOT_FOUND, MessageTypes.NOT_FOUND
        )

    @staticmethod
    def get_successfully_deleted_msg(vacancy_id: UUID) -> Dict:
        return MessageManager.make_message(
            MessageTexts.VACANCY_DELETED.format(vacancy_id),
            MessageTypes.VACANCY_DELETED,
        )

    @staticmethod
    def get_invalid_filters_msg() -> Dict:
        return MessageManager.make_message(
            MessageTexts.INVALID_FILTERS,
            MessageTypes.INVALID_FILTERS,
        )

    @staticmethod
    def get_vacancy_response_not_found_msg(vacancy_response_id: UUID) -> Dict:
        return MessageManager.make_message(
            MessageTexts.VACANCY_RESPONSE_NOT_FOUND.format(vacancy_response_id), MessageTypes.NOT_FOUND
        )

    @staticmethod
    def get_invalid_filters_response_msg() -> Dict:
        return MessageManager.make_message(
            MessageTexts.INVALID_FILTERS_RESPONSE,
            MessageTypes.INVALID_FILTERS,
        )

    @staticmethod
    def get_invalid_filters_user_response_msg() -> Dict:
        return MessageManager.make_message(
            MessageTexts.INVALID_FILTERS_USER_RESPONSES,
            MessageTypes.INVALID_FILTERS,
        )

    @staticmethod
    def get_user_responses_nothing_found_msg() -> Dict:
        return MessageManager.make_message(
            MessageTexts.USER_RESPONSES_NOT_FOUND,
            MessageTypes.NOT_FOUND
        )

    @staticmethod
    def get_gp_project_id_nothing_found_msg(gp_project_id: UUID) -> Dict:
        return MessageManager.make_message(
            MessageTexts.GP_PROJECT_ID_NOT_FOUND.format(gp_project_id),
            MessageTypes.NOT_FOUND
        )


    @staticmethod
    def get_gp_project_id_nothing_found_msg_or_unavailable_registry(gp_project_id: UUID) -> Dict:
        return MessageManager.make_message(
            MessageTexts.GP_PROJECT_ID_NOT_FOUND_OR_NOT_REGISTRY.format(gp_project_id),
            MessageTypes.NOT_FOUND
        )


    @staticmethod
    def invalid_signature() -> Dict:
        return MessageManager.make_message(
            MessageTexts.INVALID_SIGNATURE,
            MessageTypes.SIGNATURE_DONT_MATCH
        )

    @staticmethod
    def get_service_unavailable_msg(service_name: str) -> Dict:
        return MessageManager.make_message(
            MessageTexts.SERVICE_IS_UNAVAILABLE.format(service_name),
            MessageTypes.SERVICE_UNAVAILABLE
        )

    @staticmethod
    def get_successfully_notify_msg(vacancy_id: UUID) -> Dict:
        return MessageManager.make_message(
            MessageTexts.VACANCY_NOTIFIED.format(vacancy_id),
            MessageTypes.VACANCY_NOTIFY,
        )

    @staticmethod
    def get_service_validation_error(service_name: str, error_detail: Dict) -> Dict:
        return MessageManager.make_message(
            MessageTexts.SERVICE_VALIDATION_ERROR.format(service_name, error_detail),
            MessageTypes.VALIDATION_ERROR
        )

    @staticmethod
    def timeout_signature() -> Dict:
        if config.settings.SINGER_DEBUG:
            info_message = f"Now timestamp is {datetime.datetime.now().timestamp()}"
            return MessageManager.make_message(
                MessageTexts.AUTHENTICATION_TIMEOUT_ERROR.format(info_message),
                MessageTypes.AUTHENTICATION_ERROR
            )
        else:
            info_message = f"You need a new signature"
            return MessageManager.make_message(
                MessageTexts.AUTHENTICATION_TIMEOUT_ERROR.format(info_message),
                MessageTypes.AUTHENTICATION_ERROR
            )

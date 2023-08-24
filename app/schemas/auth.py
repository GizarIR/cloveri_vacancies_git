from uuid import UUID
import enum

from pydantic import BaseModel, Field
from fastapi.params import Query


class ServiceOperation(str, enum.Enum):
    VACANCIES = "vacancies"
    RESPONSES_BY_USER = "responses by user"
    RESPONSES_BY_VACANCY = "responses by vacancy"
    UPDATE_VACANCIES = "update vacancies"
    ADD_VACANCIES = "add vacancies"

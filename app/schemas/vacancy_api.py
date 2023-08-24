import enum
from typing import List

from pydantic import BaseModel

from .user_response import UserResponse
from .vacancy import Vacancy
from .vacancy_response import VacancyResponse


class SortingParam(str, enum.Enum):
    none = "none"
    name = "name"
    profession = "profession"
    created_on = "created_on"
    updated_on = "updated_on"


class SortingOrder(str, enum.Enum):
    asc = "asc"
    desc = "desc"


class VacancyPage(BaseModel):
    items: List[Vacancy]
    page: int
    limit: int


class ResponseSortingParam(str, enum.Enum):
    none = "none"
    created_on = "created_on"


class VacancyResponsePage(BaseModel):
    items: List[VacancyResponse]
    page: int
    limit: int


class UserResponsePage(BaseModel):
    items: List[UserResponse]
    page: int
    limit: int

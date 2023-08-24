from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator, EmailStr


class DataResponse(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone: str = "79991112233"
    city: str
    best_season: str
    best_status: str

    @validator("first_name")
    def validate_first_name_required(cls, v, values, **kwargs):
        if not v:
            raise ValueError("first_name is required field")
        return v

    @validator("first_name")
    def validate_first_name(cls, v, values, **kwargs):
        if v and len(v) > 150:
            raise ValueError("first_name can only contain max 150 characters")
        return v

    @validator("last_name")
    def validate_last_name_required(cls, v, values, **kwargs):
        if not v:
            raise ValueError("last_name is required field")
        return v

    @validator("last_name")
    def validate_last_name(cls, v, values, **kwargs):
        if v and len(v) > 150:
            raise ValueError("last_name can only contain max 150 characters")
        return v

    @validator("middle_name")
    def validate_middle_name(cls, v, values, **kwargs):
        if v and len(v) > 150:
            raise ValueError("middle_name can only contain max 150 characters")
        return v

    @validator("phone")
    def validate_phone(cls, v, values, **kwargs):
        if v and (len(v) > 11 or not v.isdigit()):
            raise ValueError("phone can only contain max 11 digits")
        return v

    @validator("city")
    def validate_city_required(cls, v, values, **kwargs):
        if not v:
            raise ValueError("city is required field")
        return v

    @validator("city")
    def validate_city(cls, v, values, **kwargs):
        if v and len(v) > 150:
            raise ValueError("city can only contain max 150 characters")
        return v

    @validator("best_season")
    def validate_best_season(cls, v, values, **kwargs):
        if v and len(v) > 150:
            raise ValueError("best_season can only contain max 150 characters")
        return v

    @validator("best_status")
    def validate_best_status(cls, v, values, **kwargs):
        if v and len(v) > 150:
            raise ValueError("best_status can only contain max 150 characters")
        return v


class BaseVacancyResponse(BaseModel):
    gp_project_id: UUID = Field(description="Group of companies ID project. Required.")
    gp_company_id: Optional[UUID] = Field(description="Group of companies ID company. Empty value: null")
    gp_user_id: Optional[UUID] = Field(description="Group of companies  ID user. Empty value: null. "
                                                   "The gp_user_id field or the email and phone fields "
                                                   "must be filled in field of data_response")
    vacancy_id: UUID = Field(description="ID vacancy. Required.")
    data_response: List[DataResponse] = Field(default_factory=list, description="JSON field with information about "
                                                                                "response. Empty value for any key is "
                                                                                "empty string, like this: \"\"")

    @validator('data_response')
    def data_response_not_empty(cls, v):
        if not v:
            raise ValueError("{data_response} must not be empty")
        return v

    @validator("data_response")
    def validate_user(cls, v, values, **kwargs):
        if not values['gp_user_id']:
            if not ('email' in v) and not ('phone' in v):
                raise ValueError("{gp_user_id} or {email and phone} fields must be filled in")
        return v

    class Config:
        orm_mode = True


class VacancyResponse(BaseVacancyResponse):
    id: UUID
    created_on: datetime


class CreateVacancyResponse(BaseVacancyResponse):
    pass


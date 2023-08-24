import re
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator

from .vacancy_skill import CreateVacancySkillNested, VacancySkillNested
from .vacancy_response import CreateVacancyResponse, VacancyResponse
from .user_response import UserResponse


# TODO Enum need to move to shared.py
class ContactType(str, Enum):
    email = "email"
    telegram = "telegram"
    whatsapp = "whatsapp"
    skype = "skype"
    phone = "phone"
    other = "other"


class Contact(BaseModel):
    type: ContactType
    contact: str


class Requirements(BaseModel):
    experience: str
    description: str


class Conditions(BaseModel):
    schedule: str
    employment: str
    other: str


class BaseVacancyNoSkills(BaseModel):
    name: str
    is_active: bool = False

    company_id: Optional[UUID]
    company_name: Optional[str]

    positions: Optional[int]

    requirements: List[Requirements] = Field(default_factory=list)
    conditions: List[Conditions] = Field(default_factory=list)
    responsibilities: Optional[str]

    short_description: Optional[str]
    full_description: Optional[str]
    profession_id: Optional[UUID]

    salary_from: Optional[float]
    salary_to: Optional[float]

    contact_name: Optional[str]
    contact_company: Optional[str]
    contact_position: Optional[str]
    contacts: List[Contact] = Field(default_factory=list)

    start_date: Optional[date]
    end_date: Optional[date]

    url: Optional[HttpUrl] = Field(None, example="http://mycompany.com")

    pic_main: Optional[HttpUrl] = Field(None, example="http://mycompany.com/pic.jpg")
    pic_main_dm: Optional[HttpUrl] = Field(
        None, example="http://mycompany.com/main_pic.png"
    )
    pic_recs: Optional[HttpUrl] = Field(
        None, example="http://mycompany.com/rec_pic.jpg"
    )

    region: Optional[str]

    team_ids: List[UUID] = Field(default_factory=list)

    gp_project_id: UUID
    gp_company_id: Optional[UUID]
    gp_user_id: Optional[UUID]

    comments: Optional[str]

    @validator("salary_to")
    def salary_from_must_be_smaller(cls, v, values, **kwargs):
        salary_from = values.get("salary_from", None)
        if salary_from and v and v < salary_from:
            raise ValueError("salary_from mustn't exceed salary_to")
        return v

    @validator("salary_from")
    def salary_from_large_value(cls, v, values, **kwargs):
        if v and v > 1000000000:
            raise ValueError("salary_from is too large")
        return v

    @validator("salary_to")
    def salary_to_large_value(cls, v, values, **kwargs):
        if v and v > 1000000000:
            raise ValueError("salary_to is too large")
        return v

    @validator("salary_from")
    def salary_from_must_be_positive(cls, v, values, **kwargs):
        if v and v < 0:
            raise ValueError("salary_from cannot be negative number")
        return v

    @validator("salary_to")
    def salary_to_must_be_positive(cls, v, values, **kwargs):
        if v and v < 0:
            raise ValueError("salary_to cannot be negative number")
        return v

    @validator("end_date")
    def end_date_must_be_in_future(cls, v, values, **kwargs):
        start_date = values.get("start_date", None)
        if start_date and v and start_date > v:
            raise ValueError("end_date must be later than start_date")
        return v

    @validator("positions")
    def validate_smallint(cls, v, values, **kwargs):
        if v < 0:
            raise ValueError("positions must be a positive number")
        if v > 3000:
            raise ValueError("positions number is too large (max 3000)")
        return v

    @validator("short_description")
    def validate_short_description(cls, v, values, **kwargs):
        if v and len(v) > 500:
            raise ValueError("short_description can only contain max 500 characters")
        return v

    @validator("full_description")
    def validate_full_description(cls, v, values, **kwargs):
        if v and len(v) > 500:
            raise ValueError("full_description can only contain max 500 characters")
        return v

    @validator("comments")
    def validate_comments(cls, v, values, **kwargs):
        if v and len(v) > 500:
            raise ValueError("comments can only contain max 500 characters")
        return v

    @validator("responsibilities")
    def validate_responsibilities(cls, v, values, **kwargs):
        if v and len(v) > 2000:
            raise ValueError("responsibilities can only contain max 2000 characters")
        return v

    @validator("requirements")
    def validate_requirements(cls, v, values, **kwargs):
        for req in v:
            if req.description and len(req.description) > 500:
                raise ValueError("description in requirement can only contain max 500 characters")
        return v

    @validator("conditions")
    def validate_conditions(cls, v, values, **kwargs):
        for condition in v:
            if condition.other and len(condition.other) > 500:
                raise ValueError("other in condition can only contain max 500 characters")
        return v

    @validator("contacts")
    def validate_contacts(cls, v, values, **kwargs):
        if len(v) < 1:
            raise ValueError("one of the contacts fields must be filled")
        return v

    @validator('contacts')
    def contact_alphanumeric(cls, v):
        pattern = r'[a-zA-Z0-9]'
        for contact_in in v:
            if contact_in.type == ContactType.phone \
                    and (not contact_in.contact.isdigit() or len(contact_in.contact) > 11):
                raise ValueError(f'contact {contact_in.type} must be contain only 11 digits')
            if not contact_in.contact == "" and not re.search(pattern, contact_in.contact):
                raise ValueError(f'contact {contact_in.type} must be contain letters or numbers')
        return v


    class Config:
        orm_mode = True


class BaseVacancy(BaseVacancyNoSkills):
    skills: List[VacancySkillNested] = Field(default_factory=list)

    @validator("skills")
    def validate_skills_are_unique(cls, v, values, **kwargs):
        skills = set()
        skills_descriptions = set()
        for skill in v:
            if skill.skill_id in skills:
                raise ValueError("Skills must be unique within 1 vacancy")
            # Temporary check, while don't have connection to main DB Cloveri
            if skill.skill_description in skills:
                raise ValueError("Skills must be unique within 1 vacancy")
            skills.add(skill.skill_id)
            # Temporary check, while don't have connection to main DB Cloveri
            skills_descriptions.add(skill.skill_description)
        return v


class Vacancy(BaseVacancy):
    id: UUID
    created_on: datetime
    updated_on: datetime


class CreateVacancy(BaseVacancy):
    skills: List[CreateVacancySkillNested] = Field(default_factory=list)


class EditVacancy(CreateVacancy):
    id: UUID
    skills: List[VacancySkillNested] = Field(default_factory=list)

from uuid import UUID

from pydantic import BaseModel, validator

from .shared import SkillDesirability, SkillLevel


class BaseVacancySkill(BaseModel):
    skill_id: UUID
    is_competence: bool
    skill_description: str
    desirability: SkillDesirability
    level: SkillLevel
    priority: int

    @validator("priority")
    def validate_smallint(cls, v, values, **kwargs):
        if v < 0:
            raise ValueError("priority must be a positive number")
        if v > 1000:
            raise ValueError("priority number is too large (max 1000)")
        return v

    class Config:
        orm_mode = True


class VacancySkillWithId(BaseModel):
    vacancy_id: UUID


class CreateVacancySkillNested(BaseVacancySkill):
    pass


class VacancySkillNested(BaseVacancySkill):
    pass


class CreateVacancySkill(BaseVacancySkill, VacancySkillWithId):
    pass


class VacancySkill(BaseVacancySkill, VacancySkillWithId):
    pass

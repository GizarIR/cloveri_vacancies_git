from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from pydantic.types import List
from sqlalchemy import asc, desc, update, func, cast, String, text, and_, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, aliased, join

from app.schemas.vacancy import CreateVacancy, EditVacancy
from app.schemas.vacancy_skill import VacancySkillNested
from app.schemas.vacancy_response import CreateVacancyResponse
from app.schemas.user_response import UserResponse


from ..errors import VacancyNotFoundError
from ..schemas.vacancy_api import SortingOrder, SortingParam, VacancyPage, ResponseSortingParam, VacancyResponsePage, \
    UserResponsePage
from .models import Vacancy, VacancySkill, VacancyResponse

sorting_to_field_map = {
    SortingParam.none: None,
    SortingParam.name: Vacancy.name,
    SortingParam.created_on: Vacancy.created_on,
    SortingParam.updated_on: Vacancy.updated_on,
    SortingParam.profession: Vacancy.profession_id,
}

response_sorting_to_field_map = {
    ResponseSortingParam.none: None,
    ResponseSortingParam.created_on: VacancyResponse.created_on,
}

sorting_order_map = {SortingOrder.asc: asc, SortingOrder.desc: desc}


class DAL:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_vacancy(self, vacancy_id: UUID) -> Optional[Vacancy]:
        result = await self.session.execute(
            select(Vacancy)
            .filter(Vacancy.id == vacancy_id)
            .options(selectinload(Vacancy.skills))
        )
        return result.scalar()

    async def create_vacancy(self, vacancy_create: CreateVacancy) -> Vacancy:
        vacancy_dict = vacancy_create.dict()
        skills = vacancy_dict.pop("skills")
        new_vacancy = Vacancy(**vacancy_dict)
        self.session.add(new_vacancy)

        await self.session.commit()
        for skill in skills:
            self.session.add(VacancySkill(**skill, vacancy_id=new_vacancy.id))

        await self.session.commit()
        # refresh linked models
        return await self.get_vacancy(new_vacancy.id)

    async def edit_vacancy(self, vacancy_edit: EditVacancy) -> Optional[Vacancy]:
        result = await self.get_vacancy(vacancy_edit.id)
        if not result:
            return None

        vacancy_dict = vacancy_edit.dict()
        vacancy_dict.pop("skills")
        vacancy_dict.pop("id")
        skills = result.skills
        # this expires the initial vacancy object
        result = None
        result = await self.__edit_skills(vacancy_edit.id, skills, vacancy_edit.skills)
        for var, value in vacancy_dict.items():
            setattr(result, var, value)
        await self.session.execute(update(Vacancy).where(Vacancy.id == vacancy_edit.id))
        await self.session.commit()
        return await self.get_vacancy(vacancy_edit.id)

    async def __edit_skills(
        self,
        vacancy_id,
        db_skills: List[VacancySkill],
        skills: List[VacancySkillNested],
    ):
        skill_id_to_skill = {str(skill.skill_id): skill.dict() for skill in skills}

        for db_skill in db_skills:
            if str(db_skill.skill_id) not in skill_id_to_skill:
                await self.session.delete(db_skill)
            else:
                skill_dict = skill_id_to_skill.pop(str(db_skill.skill_id))
                skill_dict.pop("skill_id")
                for var, value in skill_dict.items():
                    setattr(db_skill, var, value)

        for added_skill in skill_id_to_skill.values():
            skill = VacancySkill(**added_skill, vacancy_id=vacancy_id)
            self.session.add(skill)
        # refresh linked objects
        vacancy = await self.get_vacancy(vacancy_id)
        return vacancy

    async def get_vacancies_page(
        self,
        page: int,
        limit: int,
        gp_project_id: UUID,
        company_id: UUID,
        profession_id: UUID,
        team_id: UUID,
        sorting: SortingParam,
        order: SortingOrder,
    ) -> VacancyPage:
        query = select(Vacancy)
        if gp_project_id:
            query = query.filter(Vacancy.gp_project_id == gp_project_id)
        if company_id:
            query = query.filter(Vacancy.company_id == company_id)
        if profession_id:
            query = query.filter(Vacancy.profession_id == profession_id)
        if team_id:
            query = query.filter(Vacancy.team_ids.contains([team_id]))
        sorting_field = sorting_to_field_map[sorting]
        sorting_order = sorting_order_map[order]
        if sorting_field:
            query = query.order_by(sorting_order(sorting_field))
        query = query.options(selectinload(Vacancy.skills))
        query = query.offset(page * limit).limit(limit)

        result = await self.session.execute(query)
        return VacancyPage(items=result.scalars().all(), page=page, limit=limit)

    async def delete_vacancy(self, vacancy_id: UUID) -> None:
        result = await self.session.execute(
            select(Vacancy)
            .filter(Vacancy.id == vacancy_id)
            .options(selectinload(Vacancy.skills))
        )
        result = result.scalar_one_or_none()
        if not result:
            raise VacancyNotFoundError
        await self.session.delete(result)
        await self.session.commit()

    async def get_vacancy_response(self, vacancy_response_id: UUID) -> Optional[VacancyResponse]:
        result = await self.session.execute(
            select(VacancyResponse)
            .filter(VacancyResponse.id == vacancy_response_id)
        )
        return result.scalar()

    async def create_vacancy_response(self, vacancy_response_create: CreateVacancyResponse) -> VacancyResponse:
        vacancy_response_dict = vacancy_response_create.dict()

        new_vacancy_response = VacancyResponse(**vacancy_response_dict)

        result = await self.session.execute(
            select(Vacancy)
            .filter(Vacancy.id == new_vacancy_response.vacancy_id)
            .options(selectinload(Vacancy.skills))
        )
        result = result.scalar_one_or_none()

        if not result:
            raise VacancyNotFoundError

        self.session.add(new_vacancy_response)
        await self.session.commit()

        return await self.get_vacancy_response(new_vacancy_response.id)

    async def get_vacancy_responses_page(
        self,
        page: int,
        limit: int,
        vacancy_id: UUID,
        sorting: ResponseSortingParam,
        order: SortingOrder,
    ) -> VacancyResponsePage:
        query = select(VacancyResponse)
        if vacancy_id:
            query = query.filter(VacancyResponse.vacancy_id == vacancy_id)

        sorting_field = response_sorting_to_field_map[sorting]

        sorting_order = sorting_order_map[order]
        if sorting_field:
            query = query.order_by(sorting_order(sorting_field))
        query = query.offset(page * limit).limit(limit)

        result = await self.session.execute(query)
        return VacancyResponsePage(items=result.scalars().all(), page=page, limit=limit)

    async def get_user_responses_page(
        self,
        page: int,
        limit: int,
        gp_user_id: UUID,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: EmailStr,
        phone: str,
        sorting: ResponseSortingParam,
        order: SortingOrder,
    ) -> VacancyResponsePage:
        query = select(VacancyResponse)
        if gp_user_id:
            query = query.filter(VacancyResponse.gp_user_id == gp_user_id)
        if first_name:
            first_name_value = f'"{first_name}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['first_name'], String) == first_name_value)
        if last_name:
            last_name_value = f'"{last_name}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['last_name'], String) == last_name_value)
        if middle_name:
            middle_name_value = f'"{middle_name}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['middle_name'], String) == middle_name_value)
        if email:
            email_value = f'"{email}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['email'], String) == email_value)
        if phone:
            phone_value = f'"{phone}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['phone'], String) == phone_value)

        sorting_field = response_sorting_to_field_map[sorting]
        sorting_order = sorting_order_map[order]

        if sorting_field:
            query = query.order_by(sorting_order(sorting_field))

        query = query.offset(page * limit).limit(limit)

        result = await self.session.execute(query)
        return VacancyResponsePage(items=result.scalars().all(), page=page, limit=limit)

    async def v2_get_user_responses_page(
        self,
        page: int,
        limit: int,
        gp_user_id: UUID,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: EmailStr,
        phone: str,
        sorting: ResponseSortingParam,
        order: SortingOrder,
    ) -> UserResponsePage:

        query = select(VacancyResponse.id.label('id'),
                       VacancyResponse.created_on.label('created_on'),
                       VacancyResponse.data_response.label('data_response'),
                       VacancyResponse.vacancy_id.label('vacancy_id'),
                       VacancyResponse.gp_user_id.label('gp_user_id'),
                       Vacancy.name.label('name'),
                       Vacancy.company_name.label('company_name'),
                       )
        query = query.join(Vacancy, VacancyResponse.vacancy_id == Vacancy.id)

        if gp_user_id:
            query = query.filter(VacancyResponse.gp_user_id == gp_user_id)
        if first_name:
            first_name_value = f'"{first_name}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['first_name'], String) == first_name_value)
        if last_name:
            last_name_value = f'"{last_name}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['last_name'], String) == last_name_value)
        if middle_name:
            middle_name_value = f'"{middle_name}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['middle_name'], String) == middle_name_value)
        if email:
            email_value = f'"{email}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['email'], String) == email_value)
        if phone:
            phone_value = f'"{phone}"'
            query = query.filter(cast(VacancyResponse.data_response[0]['phone'], String) == phone_value)

        sorting_field = response_sorting_to_field_map[sorting]
        sorting_order = sorting_order_map[order]

        if sorting_field:
            query = query.order_by(sorting_order(sorting_field))

        query = query.offset(page * limit).limit(limit)

        result = await self.session.execute(query)

        user_responses = []
        for row in result:
            user_response = UserResponse(id=row.id, created_on=row.created_on, data_response=row.data_response,
                                         vacancy_id=row.vacancy_id, gp_user_id=row.gp_user_id, name=row.name,
                                         company_name=row.company_name)
            user_responses.append(user_response)

        return UserResponsePage(items=user_responses, page=page, limit=limit)

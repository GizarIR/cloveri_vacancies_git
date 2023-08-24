import uuid

import pytest
from httpx import AsyncClient

# All test coroutines in file will be treated as marked (async allowed).
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.message_manager import MessageTexts, MessageTypes
from app.db.models import Vacancy, VacancySkill

pytestmark = pytest.mark.asyncio


async def test_delete_vacancy(mock_signature_procedure, client: AsyncClient, session: AsyncSession):
    name = "Dev"
    positions = 1
    gp_project_id = str(uuid.uuid4())
    vacancy = Vacancy(name=name, positions=positions, gp_project_id=gp_project_id)
    session.add(vacancy)
    await session.commit()

    delete_vacancy = await client.delete(f"/vacancies/{vacancy.id}?signature&gp_project_id={gp_project_id}",
                                         params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
    print(delete_vacancy.json())
    assert delete_vacancy.status_code == 200
    assert delete_vacancy.json()["detail"][0] == {
        "msg": MessageTexts.VACANCY_DELETED.format(vacancy.id),
        "type": MessageTypes.VACANCY_DELETED,
    }

    get_vacancy = await client.get(f"/vacancies/{vacancy.id}?signature&gp_project_id={gp_project_id}",
                                   params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
    assert get_vacancy.status_code == 404


async def test_delete_non_existing_vacancy_404(mock_signature_procedure,
                                               client: AsyncClient, session: AsyncSession):
    gp_project_id = str(uuid.uuid4())
    non_existing_uuid = "00000000-0000-0000-0000-000000000000"
    delete_vacancy = await client.delete(f"/vacancies/{non_existing_uuid}?signature&gp_project_id={gp_project_id}",
                                         params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
    assert delete_vacancy.status_code == 404
    assert delete_vacancy.json()["detail"][0] == {
        "msg": MessageTexts.VACANCY_NOT_FOUND.format(non_existing_uuid),
        "type": MessageTypes.NOT_FOUND,
    }


async def test_delete_vacancy_deletes_skills(mock_signature_procedure,
                                             client: AsyncClient, session: AsyncSession, vacancy_skill):
    name = "Dev"
    positions = 1
    gp_project_id = str(uuid.uuid4())
    vacancy = Vacancy(name=name, positions=positions, gp_project_id=gp_project_id, skills=[])
    session.add(vacancy)
    await session.commit()
    vacancy_skill["skill_id"] = uuid.uuid4()
    vacancy_skill = VacancySkill(**vacancy_skill, vacancy_id=vacancy.id)
    session.add(vacancy_skill)
    await session.commit()

    delete_vacancy = await client.delete(f"/vacancies/{vacancy.id}?signature&gp_project_id={gp_project_id}",
                                         params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
    assert delete_vacancy.status_code == 200

    result = await session.execute(
        select(VacancySkill).filter(VacancySkill.skill_id == vacancy_skill.skill_id)
    )
    result = result.scalar_one_or_none()
    assert result is None

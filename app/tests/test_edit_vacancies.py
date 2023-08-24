import uuid
from typing import Dict

import pytest
from httpx import AsyncClient

# All test coroutines in file will be treated as marked (async allowed).
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.message_manager import MessageTexts, MessageTypes
from app.db.dal import DAL
from app.db.models import Vacancy
from app.schemas.vacancy import CreateVacancy

pytestmark = pytest.mark.asyncio


async def test_edit_vacancy(mock_signature_procedure,
                            client: AsyncClient, session: AsyncSession, empty_vacancy: Dict, full_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()
    full_vacancy["id"] = str(vacancy.id)
    gp_project_id = str(uuid.uuid4())
    edit_vacancy = await client.put(f"/vacancies/{vacancy.id}?signature&gp_project_id={gp_project_id}",
                                    json=full_vacancy,
                                    params={"project_id": str(uuid.uuid4()), "service": "update vacancies"})
    assert edit_vacancy.status_code == 200
    edit_vacancy_json = edit_vacancy.json()
    for field, value in full_vacancy.items():
        assert edit_vacancy_json[field] == value
    assert edit_vacancy_json["id"] == str(vacancy.id)
    assert edit_vacancy_json["created_on"] != edit_vacancy_json["updated_on"]


async def test_edit_from_full_to_empty(mock_signature_procedure,
                                       client: AsyncClient, session: AsyncSession, empty_vacancy: Dict,
                                       full_vacancy: Dict):
    vacancy = Vacancy(**CreateVacancy(**full_vacancy).dict())
    session.add(vacancy)
    await session.commit()
    empty_vacancy["id"] = str(vacancy.id)
    gp_project_id = str(uuid.uuid4())
    edit_vacancy = await client.put(f"/vacancies/{vacancy.id}?signature&gp_project_id={gp_project_id}",
                                    json=empty_vacancy,
                                    params={"project_id": str(uuid.uuid4()), "service": "update vacancies"})
    assert edit_vacancy.status_code == 200
    edit_vacancy_json = edit_vacancy.json()

    for field, value in empty_vacancy.items():
        assert edit_vacancy_json[field] == value
    assert edit_vacancy_json["id"] == str(vacancy.id)


async def test_edit_skills(mock_signature_procedure,
                           client: AsyncClient,
                           session: AsyncSession,
                           vacancy_skill,
                           empty_vacancy_with_skills,
                           full_vacancy,
                           ):
    vac = await DAL(session).create_vacancy(CreateVacancy(**empty_vacancy_with_skills))
    edited_vacancy = empty_vacancy_with_skills
    edited_vacancy["id"] = str(vac.id)
    for field, value in full_vacancy.items():
        edited_vacancy[field] = value

    removed_skill = edited_vacancy["skills"].pop(1)
    edited_skill = {
        "skill_id": "46c1b999-4d9f-40b2-92a2-59a51fc9571b",
        "is_competence": False,
        "skill_description": "string",
        "desirability": "DESIRED",
        "level": "MIDDLE",
        "priority": 2,
    }

    edited_vacancy["skills"][0] = edited_skill

    added_skill = {
        "skill_id": str(uuid.uuid4()),
        "is_competence": True,
        "skill_description": "str",
        "desirability": "EMPTY",
        "level": "SENIOR",
        "priority": 20,
    }

    edited_vacancy["skills"].append(added_skill)
    gp_project_id = str(uuid.uuid4())
    edit_vacancy_result = await client.put(
        f"/vacancies/{str(vac.id)}?signature&gp_project_id={gp_project_id}", json=edited_vacancy,
        params={"project_id": str(uuid.uuid4()), "service": "update vacancies"}
    )
    assert edit_vacancy_result.status_code == 200
    edit_vacancy_dict = edit_vacancy_result.json()
    edited_skills = edit_vacancy_dict.pop("skills")
    edit_vacancy_dict.pop("created_on")
    edit_vacancy_dict.pop("updated_on")
    edited_vacancy.pop("skills")
    assert edit_vacancy_dict == edited_vacancy

    assert len(edited_skills) == 2
    assert removed_skill not in edited_skills
    assert added_skill in edited_skills

    assert edited_skills == [added_skill, edited_skill]


async def test_non_matching_uuid_raises_400(mock_signature_procedure, client: AsyncClient, empty_vacancy):
    some_id = uuid.uuid4()
    empty_vacancy["id"] = str(uuid.uuid4())
    gp_project_id = str(uuid.uuid4())
    edit_vacancy = await client.put(f"/vacancies/{some_id}?signature&gp_project_id={gp_project_id}", json=empty_vacancy,
                                    params={"project_id": str(uuid.uuid4()), "service": "update vacancies"})
    assert edit_vacancy.status_code == 400
    assert edit_vacancy.json()["detail"][0] == {
        "msg": MessageTexts.IDS_DONT_MATCH,
        "type": MessageTypes.IDS_DONT_MATCH,
    }


async def test_vacancy_not_found(mock_signature_procedure, client: AsyncClient, empty_vacancy):
    non_existing_uuid = "00000000-0000-0000-0000-000000000000"
    empty_vacancy["id"] = non_existing_uuid
    gp_project_id = str(uuid.uuid4())
    edit_vacancy = await client.put(
        f"/vacancies/{non_existing_uuid}?signature&gp_project_id={gp_project_id}", json=empty_vacancy,
        params={"project_id": str(uuid.uuid4()), "service": "update vacancies"}
    )
    assert edit_vacancy.status_code == 404
    assert edit_vacancy.json()["detail"][0] == {
        "msg": MessageTexts.VACANCY_NOT_FOUND.format(non_existing_uuid),
        "type": MessageTypes.NOT_FOUND,
    }


async def test_invalid_uuid(mock_signature_procedure, client: AsyncClient, empty_vacancy, vacancy_skill):
    invalid_uuid = "1"
    empty_vacancy["id"] = invalid_uuid
    gp_project_id = str(uuid.uuid4())
    edit_vacancy = await client.put(f"/vacancies/{invalid_uuid}?signature&gp_project_id={gp_project_id}",
                                    json=empty_vacancy,
                                    params={"project_id": str(uuid.uuid4()), "service": "update vacancies"})
    assert edit_vacancy.status_code == 422

import uuid

import pytest
from httpx import AsyncClient
from typing import Dict
# All test coroutines in file will be treated as marked (async allowed).
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Vacancy, VacancyResponse

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True, scope="function")
def _teardown(clean_db_on_setup):
    yield


async def test_get_vacancy_responses_valid(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                           empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(f"/vacancies/responses/{vacancy_response.id}?signature&gp_project_id={gp_project_id}",
                                params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert response.status_code == 200
    data = response.json()
    assert "data_response" in data
    assert isinstance(data["data_response"], list)
    assert len(data["data_response"]) == 1
    assert data["data_response"][0] == vacancy_response_full["data_response"][0]
    assert "id" in data
    assert data["id"] == str(vacancy_response.id)
    assert "gp_project_id" in data
    assert data["gp_project_id"] == str(vacancy_response.gp_project_id)
    assert "gp_company_id" in data
    assert data["gp_company_id"] == str(vacancy_response.gp_company_id)
    assert "gp_user_id" in data
    assert data["gp_user_id"] == str(vacancy_response.gp_user_id)
    assert "vacancy_id" in data
    assert data["vacancy_id"] == str(vacancy_response.vacancy_id)


async def test_get_vacancy_responses_not_found(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                               empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    nonexistent_response_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/vacancies/responses/{nonexistent_response_id}?signature&gp_project_id={gp_project_id}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"][0] == {'msg': f"Vacancy's response {nonexistent_response_id} is not found",
                                 'type': 'not_found'}


async def test_get_invalid_vacancy_response(client: AsyncClient, session: AsyncSession,
                                            empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    invalid_response_id = "invalid_response_id"
    response = await client.get(f"/vacancies/responses/{invalid_response_id}?signature&gp_project_id={gp_project_id}",
                                params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})

    assert response.status_code == 422

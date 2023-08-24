import uuid
from typing import Dict
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Vacancy, VacancyResponse

# All test coroutines in file will be treated as marked (async allowed).
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

    response = await client.get(f"/vacancies/{vacancy.id}/responses/?signature&gp_project_id={gp_project_id}",
                                params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 1
    assert "data_response" in data["items"][0]
    assert isinstance(data["items"][0]["data_response"], list)
    assert len(data["items"][0]["data_response"]) == 1
    assert data["items"][0]["data_response"][0] == vacancy_response_full["data_response"][0]


async def test_get_nonexistent_vacancy_responses(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                                 empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    nonexistent_vacancy_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(
        f"/vacancies/{nonexistent_vacancy_id}/responses/?signature&gp_project_id={gp_project_id}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"][0] == {
        "msg": "No responses for this vacancy found for chosen filters",
        "type": "not_found"
    }


async def test_get_invalid_vacancy_response(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
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
    response = await client.get(f"/vacancies/{invalid_response_id}/responses/?signature&gp_project_id={gp_project_id}",
                                params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})

    assert response.status_code == 422

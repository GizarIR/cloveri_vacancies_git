import uuid
from typing import Dict
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.message_manager import MessageTexts, MessageTypes
from app.db.models import Vacancy, VacancyResponse

# All test coroutines in file will be treated as marked (async allowed).
pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True, scope="function")
def _teardown(clean_db_on_setup):
    yield


async def test_get_user_response_valid_gp_user_id(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                                  empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    gp_user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(
        f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&gp_user_id={gp_user_id}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by user"}
    )

    assert response.status_code == 200


async def test_get_user_response_valid_first_name(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                                  empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    first_name = "string"
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(
        f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&first_name={first_name}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by user"}
    )

    assert response.status_code == 200


async def test_get_user_response_valid_last_name(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                                 empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    last_name = "string"
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(
        f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&last_name={last_name}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by user"}
    )

    assert response.status_code == 200


async def test_get_user_response_valid_middle_name(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                                   empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    middle_name = "string"
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(
        f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&middle_name={middle_name}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by user"}
    )

    assert response.status_code == 200


async def test_get_user_response_valid_email(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                             empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    email = "user@example.com"
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&email={email}",
                                params={"project_id": str(uuid.uuid4()), "service": "responses by user"})

    assert response.status_code == 200


async def test_get_user_response_valid_phone(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                             empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    phone = "87123456789"
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&phone={phone}",
                                params={"project_id": str(uuid.uuid4()), "service": "responses by user"})

    assert response.status_code == 200


async def test_get_user_response_400(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                     empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(
        f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by user"}
    )
    assert response.status_code == 400
    assert response.json()["detail"][0] == {
        "msg": MessageTexts.INVALID_FILTERS_USER_RESPONSES,
        "type": MessageTypes.INVALID_FILTERS
    }


async def test_get_user_response_422(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                     empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    gp_user_id = 123
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(
        f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&gp_user_id={gp_user_id}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by user"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0] == {'loc': ['query', 'gp_user_id'],
                                            'msg': 'value is not a valid uuid',
                                            'type': 'type_error.uuid'}


async def test_get_user_response_404(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                     empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full["vacancy_id"] = vacancy.id
    gp_project_id = str(uuid.uuid4())
    gp_user_id = "3fa85f64-0000-0000-0000-2c963f66afa6"
    vacancy_response = VacancyResponse(**vacancy_response_full)
    session.add(vacancy_response)
    await session.commit()

    response = await client.get(
        f"/vacancies/responses/users/?signature&gp_project_id={gp_project_id}&gp_user_id={gp_user_id}",
        params={"project_id": str(uuid.uuid4()), "service": "responses by user"}
    )
    assert response.status_code == 404
    assert response.json()["detail"][0] == {
        "msg": MessageTexts.USER_RESPONSES_NOT_FOUND,
        "type": MessageTypes.NOT_FOUND
    }

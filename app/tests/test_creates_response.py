import uuid
import json
from typing import Dict
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Vacancy

# All test coroutines in file will be treated as marked (async allowed).
pytestmark = pytest.mark.asyncio


async def test_create_vacancy_response(mock_signature_procedure, client: AsyncClient, session: AsyncSession,
                                       empty_vacancy: Dict):
    vac = Vacancy(name="Example", positions=5, gp_company_id=str(uuid.uuid4()), profession_id=str(uuid.uuid4()),
                  gp_project_id=str(uuid.uuid4()), gp_user_id=str(uuid.uuid4()))
    session.add(vac)
    await session.commit()
    vacancy_response_full = {"gp_project_id": str(vac.gp_project_id),
                             "gp_company_id": str(vac.gp_company_id),
                             "gp_user_id": str(vac.gp_user_id),
                             "vacancy_id": str(vac.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "Петров",
                                     "middle_name": "Васильевич",
                                     "email": "user@example.com",
                                     "phone": "87123456789",
                                     "city": "Москва",
                                     "best_season": "1 сезон",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }

    data_fields = json.dumps(vacancy_response_full)
    create_vacancy_response = await client.post(f"/vacancies/responses/?signature", content=data_fields,
                                                headers={"Content-Type": "application/json"},
                                                params={"project_id": str(uuid.uuid4()),
                                                        "service": "responses by vacancy"})
    assert create_vacancy_response.status_code == 201
    created_vacancy = create_vacancy_response.json()
    assert created_vacancy["data_response"][0]["first_name"] == vacancy_response_full["data_response"][0]["first_name"]
    assert created_vacancy["data_response"][0]["last_name"] == vacancy_response_full["data_response"][0]["last_name"]
    assert created_vacancy["data_response"][0]["middle_name"] == vacancy_response_full["data_response"][0][
        "middle_name"]
    assert created_vacancy["data_response"][0]["email"] == vacancy_response_full["data_response"][0]["email"]
    assert created_vacancy["data_response"][0]["phone"] == vacancy_response_full["data_response"][0]["phone"]
    assert created_vacancy["data_response"][0]["city"] == vacancy_response_full["data_response"][0]["city"]
    assert created_vacancy["data_response"][0]["best_season"] == vacancy_response_full["data_response"][0][
        "best_season"]
    assert created_vacancy["data_response"][0]["best_status"] == vacancy_response_full["data_response"][0][
        "best_status"]


async def test_create_vacancy_response2(mock_signature_procedure, client: AsyncClient,
                                        session: AsyncSession,
                                        empty_vacancy: Dict, vacancy_response_full):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()
    vacancy_response_full["vacancy_id"] = str(vacancy.id)
    data_fields = json.dumps(vacancy_response_full)
    vacancy_response = await client.post(f"/vacancies/responses/?signature", content=data_fields,
                                         headers={"Content-Type": "application/json"},
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    print(vacancy_response.json())

    assert vacancy_response.status_code == 201
    created_vacancy = vacancy_response.json()
    assert created_vacancy["data_response"][0]["first_name"] == vacancy_response_full["data_response"][0]["first_name"]
    assert created_vacancy["data_response"][0]["last_name"] == vacancy_response_full["data_response"][0]["last_name"]
    assert created_vacancy["data_response"][0]["middle_name"] == vacancy_response_full["data_response"][0][
        "middle_name"]
    assert created_vacancy["data_response"][0]["email"] == vacancy_response_full["data_response"][0]["email"]
    assert created_vacancy["data_response"][0]["phone"] == vacancy_response_full["data_response"][0]["phone"]
    assert created_vacancy["data_response"][0]["city"] == vacancy_response_full["data_response"][0]["city"]
    assert created_vacancy["data_response"][0]["best_season"] == vacancy_response_full["data_response"][0][
        "best_season"]
    assert created_vacancy["data_response"][0]["best_status"] == vacancy_response_full["data_response"][0][
        "best_status"]


async def test_create_vacancy_response_invalid_vacancy(mock_signature_procedure, client: AsyncClient,
                                                       session: AsyncSession,
                                                       empty_vacancy: Dict, vacancy_response_full):
    vac = Vacancy(name="Example", positions=5, gp_company_id=str(uuid.uuid4()), profession_id=str(uuid.uuid4()),
                  gp_project_id=str(uuid.uuid4()), gp_user_id=str(uuid.uuid4()))
    session.add(vac)
    await session.commit()

    vacancy_response_full["gp_project_id"] = str(vac.gp_project_id)
    json_data = json.dumps(vacancy_response_full)
    vacancy_response = await client.post(f"/vacancies/responses/?signature", content=json_data,
                                         headers={"Content-Type": "application/json"},
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 404


async def test_create_vacancy_response_missing_field_first_name(mock_signature_procedure, client: AsyncClient,
                                                                session: AsyncSession,
                                                                empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "",
                                     "last_name": "Петров",
                                     "middle_name": "Васильевич",
                                     "email": "user@example.com",
                                     "phone": "87123456789",
                                     "city": "Москва",
                                     "best_season": "1 сезон",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 422


async def test_create_vacancy_response_missing_field_last_name(mock_signature_procedure, client: AsyncClient,
                                                               session: AsyncSession,
                                                               empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "",
                                     "middle_name": "Васильевич",
                                     "email": "user@example.com",
                                     "phone": "87123456789",
                                     "city": "Москва",
                                     "best_season": "1 сезон",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 422


async def test_create_vacancy_response_missing_field_middle_name(mock_signature_procedure, client: AsyncClient,
                                                                 session: AsyncSession,
                                                                 empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "Петров",
                                     "middle_name": "",
                                     "email": "user@example.com",
                                     "phone": "87123456789",
                                     "city": "Москва",
                                     "best_season": "1 сезон",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 201


async def test_create_vacancy_response_missing_field_email(mock_signature_procedure, client: AsyncClient,
                                                           session: AsyncSession,
                                                           empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "Петров",
                                     "middle_name": "Васильевич",
                                     "email": "",
                                     "phone": "87123456789",
                                     "city": "Москва",
                                     "best_season": "1 сезон",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 422


async def test_create_vacancy_response_missing_field_phone(mock_signature_procedure, client: AsyncClient,
                                                           session: AsyncSession,
                                                           empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "Петров",
                                     "middle_name": "Васильевич",
                                     "email": "user@example.com",
                                     "phone": "",
                                     "city": "Москва",
                                     "best_season": "1 сезон",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 201


async def test_create_vacancy_response_missing_field_city(mock_signature_procedure, client: AsyncClient,
                                                          session: AsyncSession,
                                                          empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "Петров",
                                     "middle_name": "Васильевич",
                                     "email": "user@example.com",
                                     "phone": "87123456789",
                                     "city": "",
                                     "best_season": "1 сезон",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 422


async def test_create_vacancy_response_missing_field_best_season(mock_signature_procedure, client: AsyncClient,
                                                                 session: AsyncSession,
                                                                 empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "Петров",
                                     "middle_name": "Васильевич",
                                     "email": "user@example.com",
                                     "phone": "87123456789",
                                     "city": "Москва",
                                     "best_season": "",
                                     "best_status": "Полуфиналист"
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 201


async def test_create_vacancy_response_missing_field_best_status(mock_signature_procedure, client: AsyncClient,
                                                                 session: AsyncSession,
                                                                 empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()

    vacancy_response_full = {"gp_project_id": str(vacancy.gp_project_id),
                             "gp_company_id": str(vacancy.gp_company_id),
                             "gp_user_id": str(vacancy.gp_user_id),
                             "vacancy_id": str(vacancy.id),
                             "data_response": [
                                 {
                                     "first_name": "Иван",
                                     "last_name": "Петров",
                                     "middle_name": "Васильевич",
                                     "email": "user@example.com",
                                     "phone": "87123456789",
                                     "city": "Москва",
                                     "best_season": "1 сезон",
                                     "best_status": ""
                                 }
                             ]
                             }
    vacancy_response = await client.post(f"/vacancies/responses/?signature", json=vacancy_response_full,
                                         params={"project_id": str(uuid.uuid4()), "service": "responses by vacancy"})
    assert vacancy_response.status_code == 201

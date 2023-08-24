import uuid

import pytest
from httpx import AsyncClient
from typing import Dict
# All test coroutines in file will be treated as marked (async allowed).
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.message_manager import MessageTexts, MessageTypes
from app.db.models import Vacancy
from app.session import async_session

pytestmark = pytest.mark.asyncio


async def test_get_vacancy(mock_signature_procedure, client: AsyncClient, session: AsyncSession, empty_vacancy: Dict):
    vacancy = Vacancy(**empty_vacancy)
    session.add(vacancy)
    await session.commit()
    gp_project_id = str(uuid.uuid4())
    get_vacancy = await client.get(f"/vacancies/{vacancy.id}?signature&gp_project_id={gp_project_id}",
                                   params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
    assert get_vacancy.status_code == 200
    get_vacancy_json = get_vacancy.json()
    assert get_vacancy_json["name"] == "Cloveri"
    assert get_vacancy_json["positions"] == 0
    assert get_vacancy_json["id"] == str(vacancy.id)
    assert get_vacancy_json["created_on"] == get_vacancy_json["updated_on"]


async def test_vacancy_not_found(mock_signature_procedure, client: AsyncClient, full_vacancy):
    non_existing_uuid = "00000000-0000-0000-0000-000000000000"
    gp_project_id = str(uuid.uuid4())
    get_vacancy = await client.get(f"/vacancies/{non_existing_uuid}?signature&gp_project_id={gp_project_id}",
                                   params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
    assert get_vacancy.status_code == 404
    assert get_vacancy.json()["detail"][0] == {
        "msg": MessageTexts.VACANCY_NOT_FOUND.format(non_existing_uuid),
        "type": MessageTypes.NOT_FOUND,
    }


async def test_invalid_uuid(client: AsyncClient, full_vacancy, vacancy_skill):
    invalid_uuid = "1"
    gp_project_id = str(uuid.uuid4())
    get_vacancy = await client.get(f"/vacancies/{invalid_uuid}?signature&gp_project_id={gp_project_id}",
                                   params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
    assert get_vacancy.status_code == 422


class TestPaging:
    gp_project_id = str(uuid.uuid4())
    profession_id = str(uuid.uuid4())
    team_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())

    @pytest.fixture(scope="class", autouse=True)
    async def setup(self):

        async with async_session() as session:
            vacancies = []
            vacancy_template = {
                "name": "vacancy",
                "positions": 10,
                "gp_project_id": self.gp_project_id,
                "contacts": [
                    {"type": "email",
                     "contact": "string@ya.ru"}
                ],
            }

            vacancy = vacancy_template.copy()
            vacancy["name"] = "111"
            vacancy["profession_id"] = self.profession_id
            vacancy["gp_project_id"] = self.gp_project_id
            vacancy["company_id"] = self.company_id
            vacancies.append(vacancy)

            for i in range(30):
                vacancy = vacancy_template.copy()
                vacancy["name"] = str(i)
                vacancy["gp_project_id"] = self.gp_project_id
                vacancy["company_id"] = self.company_id
                vacancies.append(vacancy)

            # add 2 objs with preset team_id
            for i in range(2):
                vacancy = vacancy_template.copy()
                vacancy["name"] = str(i)
                vacancy["gp_project_id"] = self.gp_project_id
                vacancy["profession_id"] = self.profession_id
                vacancy["company_id"] = self.company_id
                vacancy["team_ids"] = [
                    self.team_id,
                ]
                vacancies.append(vacancy)

            # 2 objects to test profession sort
            vacancy = vacancy_template.copy()
            vacancy["name"] = "222"
            vacancy["profession_id"] = self.profession_id
            vacancy["gp_project_id"] = self.gp_project_id
            vacancies.append(vacancy)

            vacancy = vacancy_template.copy()
            vacancy["name"] = "222"
            vacancies.append(vacancy)

            for vacancy in vacancies:
                session.add(Vacancy(**vacancy))
            await session.commit()
            vac = Vacancy(name="lol", positions=5, company_id=str(uuid.uuid4()), profession_id=str(uuid.uuid4()),
                          gp_project_id=str(uuid.uuid4()))
            session.add(vac)
            await session.commit()

    async def test_get_vacancies_page_with_show_all(self, client: AsyncClient, session: AsyncSession,
                                                    mock_signature_procedure):
        result = await client.get(f"/vacancies/?signature&show_all=1&limit=30",
                                  params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
        assert result.status_code == 200
        page = result.json()
        assert len(page["items"]) == 30

    async def test_get_page_invalid_filters_returns_400(self, client: AsyncClient, session: AsyncSession,
                                                        mock_signature_procedure):
        result = await client.get(f"/vacancies/?signature&limit=10",
                                  params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
        assert result.status_code == 400
        page = result.json()
        assert page["detail"][0] == {
            "msg": MessageTexts.INVALID_FILTERS,
            "type": MessageTypes.INVALID_FILTERS,
        }

    async def test_get_vacancies_page_with_profession_filter_desc(self, client: AsyncClient, session: AsyncSession,
                                                                  mock_signature_procedure):
        result = await client.get(
            f"/vacancies/?signature&sort_by=name&sort_order=desc&profession_id={self.profession_id}",
            params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
        assert result.status_code == 200
        page = result.json()
        assert len(page["items"]) == 4
        assert page["items"][0]["name"] == "222"
        assert page["items"][1]["name"] == "111"

    async def test_get_vacancies_page_with_company_filter_asc(self, client: AsyncClient, session: AsyncSession,
                                                              mock_signature_procedure):
        result = await client.get(
            f"/vacancies/?signature&sort_by=profession&company_id={self.company_id}",
            params={"project_id": str(uuid.uuid4()), "service": "vacancies"}
        )
        assert result.status_code == 200
        page = result.json()
        assert len(page["items"]) == 33
        assert page["items"][0]["profession_id"] == str(self.profession_id)
        assert page["items"][3]["profession_id"] is None
        assert page["items"][-1]["profession_id"] is None

    async def test_get_vacancies_page_with_team_filter(self, client: AsyncClient, session: AsyncSession,
                                                       mock_signature_procedure):
        result = await client.get(f"/vacancies/?signature&team_id={self.team_id}",
                                  params={"project_id": str(uuid.uuid4()), "service": "vacancies"})
        assert result.status_code == 200
        page = result.json()
        assert len(page["items"]) == 2
        assert page["items"][0]["team_ids"] == [str(self.team_id)]
        assert page["items"][-1]["team_ids"] == [str(self.team_id)]

    async def test_get_vacancies_page_desc(self, client: AsyncClient, session: AsyncSession, mock_signature_procedure):
        result = await client.get(
            f"/vacancies/?signature&page=3&limit=10&sort_by=profession&sort_order=desc&company_id={self.company_id}",
            params={"project_id": str(uuid.uuid4()), "service": "vacancies"}
        )
        assert result.status_code == 200
        page = result.json()
        assert len(page["items"]) == 3
        assert page["items"][0]["profession_id"] >= page["items"][1]["profession_id"]
        assert page["items"][1]["profession_id"] >= page["items"][2]["profession_id"]

    async def test_get_empty_page_returns_404(self, client: AsyncClient, session: AsyncSession,
                                              mock_signature_procedure):
        result = await client.get(
            f"/vacancies/?signature&page=100&sort_by=name&sort_order=desc&profession_id={self.profession_id}",
            params={"project_id": str(uuid.uuid4()), "service": "vacancies"}
        )
        assert result.status_code == 404
        assert result.json()["detail"][0] == {
            "msg": MessageTexts.VACANCIES_NOT_FOUND,
            "type": MessageTypes.NOT_FOUND,
        }

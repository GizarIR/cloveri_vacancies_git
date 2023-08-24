import uuid

import pytest
from httpx import AsyncClient

# All test coroutines in file will be treated as marked (async allowed).
pytestmark = pytest.mark.asyncio


async def test_create_simple_vacancy(mock_signature_procedure, client: AsyncClient):
    name = "Dev"
    positions = 1
    gp_project_id = str(uuid.uuid4())

    create_vacancy = await client.post(
        "/vacancies/?signature&time",
        json={"name": name, "positions": positions,
              "contacts": [
                  {"type": "email",
                   "contact": "string@ya.ru"}
              ],
              "gp_project_id": gp_project_id,
              },
        params={"project_id": str(uuid.uuid4()), "service": "add vacancies"}
    )
    print(create_vacancy.json())
    assert create_vacancy.status_code == 201
    create_vacancy_json = create_vacancy.json()
    assert create_vacancy_json["name"] == name
    assert create_vacancy_json["positions"] == positions
    assert "id" in create_vacancy_json
    assert create_vacancy_json["created_on"] == create_vacancy_json["updated_on"]


# TODO: parametrize
async def test_create_full_vacancy(mock_signature_procedure, client: AsyncClient, full_vacancy):
    create_vacancy = await client.post(
        "/vacancies/?signature",
        json=full_vacancy, params={"project_id": str(uuid.uuid4()), "service": "add vacancies"}
    )
    assert create_vacancy.status_code == 201
    created_vacancy = create_vacancy.json()
    assert "id" in created_vacancy
    assert created_vacancy["created_on"] == created_vacancy["updated_on"]
    for key in full_vacancy:
        assert created_vacancy[key] == full_vacancy[key]


async def test_create_vacancy_with_skills(mock_signature_procedure,
                                          client: AsyncClient, full_vacancy, vacancy_skill):
    full_vacancy["skills"] = [vacancy_skill]
    create_vacancy = await client.post(
        "/vacancies/?signature",
        json=full_vacancy, params={"project_id": str(uuid.uuid4()), "service": "add vacancies"}
    )
    assert create_vacancy.status_code == 201
    created_vacancy = create_vacancy.json()
    assert "id" in created_vacancy
    assert created_vacancy["created_on"] == created_vacancy["updated_on"]
    for key in full_vacancy:
        assert created_vacancy[key] == full_vacancy[key]


@pytest.mark.parametrize(
    "fields, result, error_field",
    [
        ({"positions": -10}, 422, "positions"),
        ({"positions": 0}, 201, None),
        ({"short_description": "chars" * 101}, 422, "short_description"),
        ({"url": "noturl"}, 422, "url"),
        ({"start_date": "2021-05-01", "end_date": "2021-05-02"}, 201, ""),
        ({"start_date": "2021-05-01", "end_date": "2021-05-01"}, 201, ""),
        ({"start_date": "2021-05-01", "end_date": "2021-04-02"}, 422, "end_date"),
        ({"end_date": "2021-05-02"}, 201, ""),
        ({"start_date": "2021-05-01"}, 201, ""),
        ({"salary_from": 10000, "salary_to": 10000}, 201, ""),
        ({"salary_from": 10000, "salary_to": 10001}, 201, ""),
        ({"salary_from": 10001, "salary_to": 10000}, 422, "salary_to"),
        ({"salary_from": 10000}, 201, ""),
        ({"salary_to": 10000}, 201, ""),
        ({"salary_from": -1}, 422, "salary_from"),
        ({"salary_to": -1}, 422, "salary_to"),
        ({"salary_from": 10000000000}, 422, "salary_from"),
        ({"salary_to": 10000000000}, 422, "salary_to"),
        (
                {
                    "skills": [
                        {
                            "skill_id": "48cb6fbf-d91a-e6f9-ebbc-b8cde573a290",
                            "is_competence": True,
                            "skill_description": "string",
                            "desirability": "DESIRED",
                            "level": "EXPERT",
                            "priority": 63,
                        },
                        {
                            "skill_id": "48cb6fbf-d91a-e6f9-ebbc-b8cde573a290",
                            "is_competence": False,
                            "skill_description": "string",
                            "desirability": "DESIRED",
                            "level": "EMPTY",
                            "priority": 98,
                        },
                    ]
                },
                422,
                "skills",
        ),
        (
                {
                    "skills": [
                        {
                            "skill_id": "48cb6fbf-d91a-e6f9-ebbc-b8cde573a290",
                            "is_competence": True,
                            "skill_description": "string",
                            "desirability": "DESIRED",
                            "level": "EXPERT",
                            "priority": 630009,
                        },
                    ]
                },
                422,
                "skills",
        ),
    ],
)
async def test_vacancy_validators(mock_signature_procedure,
                                  client: AsyncClient, empty_vacancy, fields, result, error_field):
    empty_vacancy.update(fields)
    create_vacancy = await client.post(
        "/vacancies/?signature",
        json=empty_vacancy, params={"project_id": str(uuid.uuid4()), "service": "add vacancies"}
    )
    assert create_vacancy.status_code == result
    if result == 422:
        errors = [detail["loc"][1] for detail in create_vacancy.json()["detail"]]
        assert errors == [error_field]


async def test_very_invalid_input(mock_signature_procedure, client: AsyncClient):
    _input = {
        "name": "proident dolor exercitation ullamco culpa",
        "positions": -37148665,
        "is_active": False,
        "company_id": "1b99266e-5c1b-0d10-b14a-a45eeb607ebd",
        "short_description": "qui ipsum tempor irure in",
        "full_description": "dolor sunt enim magna",
        "profession_id": "7191a121-3d06-d952-f0f4-ccbbf9a984e5",
        "salary_from": 77564874.18359536,
        "salary_to": -40177214.43783286,
        "contact_name": "elit Duis sunt Excepteur",
        "contacts": [
            {"type": "email", "contact": "dolor eiusmod"},
            {"type": "telegram", "contact": "in consequat cillum"},
        ],
        "start_date": "1999-08-15",
        "end_date": "1987-02-18",
        "url": "elit in reprehenderit enim",
        "pic_main": "est enim in",
        "pic_main_dm": "irure",
        "pic_recs": "laboris ex anim eu",
        "region": "occaecat consectetur ",
        "team_ids": [
            "8032249e-14da-609a-7add-8a82e167aa8c",
            "089d8e5a-b88e-f7d3-bc3b-a7dc73bb30c3",
        ],
        "skills": [
            {
                "skill_id": "48cb6fbf-d91a-e6f9-ebbc-b8cde573a290",
                "is_competence": True,
                "desirability": "DESIRED",
                "level": "EXPERT",
                "priority": 63357053,
            },
            {
                "skill_id": "f59a4d24-99a4-50d3-fc9e-20d5f49aaff6",
                "is_competence": False,
                "desirability": "DESIRED",
                "level": "EMPTY",
                "priority": 9842672,
            },
            {
                "skill_id": "a59a4d24-99a4-50d3-fc9e-20d5f49aaff6",
                "is_competence": False,
                "desirability": "REQUIRED",
                "level": "EMPTY",
                "priority": 200,
            },
            {
                "skill_id": "a59a4d24-99a4-50d3-fc9e-20d5f49aaff6",
                "is_competence": False,
                "desirability": "DESIRED",
                "level": "EMPTY",
                "priority": 200,
            },
        ],
    }
    expected_errors = [
        "positions",
        "salary_to",
        "end_date",
        "url",
        "pic_main",
        "pic_main_dm",
        "pic_recs",
        "gp_project_id",
        "skills",
        "skills",
        "skills",
        "skills",
        "skills",
        "skills",
    ]

    create_vacancy = await client.post(
        "/vacancies/?signature",
        json=_input, params={"project_id": str(uuid.uuid4()), "service": "add vacancies"}
    )
    assert create_vacancy.status_code == 422
    errors = [detail["loc"][1] for detail in create_vacancy.json()["detail"]]
    assert errors == expected_errors

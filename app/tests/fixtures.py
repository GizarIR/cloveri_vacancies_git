import pytest


@pytest.fixture()
def empty_vacancy():
    return {
        "name": "Cloveri",
        "is_active": False,
        "company_id": "4577ca61-acf9-43eb-85e4-8254d38fb3d0",
        "company_name": "Example",
        "positions": 0,
        "short_description": None,
        "full_description": None,
        "profession_id": None,
        "salary_from": None,
        "salary_to": None,
        "contact_name": None,
        "contacts": [
            {"type": "email",
             "contact": "string@ya.ru"}
        ],
        "start_date": None,
        "end_date": None,
        "url": None,
        "pic_main": None,
        "pic_main_dm": None,
        "pic_recs": None,
        "region": None,
        "team_ids": [],
        "gp_project_id": "4577ca61-acf9-43eb-85e4-8254d38fb3d0",
        "skills": [],
        "gp_user_id": "4577ca61-acf9-43eb-85e4-8254d38fb3d0",
        "gp_company_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }


@pytest.fixture()
def full_vacancy():
    return {
        "name": "string",
        "is_active": False,
        "company_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "company_name": "string",
        "positions": 0,
        "requirements": [
            {
                "experience": "string",
                "description": "string"
            }
        ],
        "conditions": [
            {
                "schedule": "string",
                "employment": "string",
                "other": "string"
            }
        ],
        "responsibilities": "string",
        "short_description": "string",
        "full_description": "string",
        "profession_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "salary_from": 0,
        "salary_to": 0,
        "contact_name": "string",
        "contact_company": "string",
        "contact_position": "string",
        "contacts": [
            {
                "type": "email",
                "contact": "string@ya.com"
            }
        ],
        "start_date": "2023-04-13",
        "end_date": "2023-04-13",
        "url": "http://mycompany.com",
        "pic_main": "http://mycompany.com/pic.jpg",
        "pic_main_dm": "http://mycompany.com/main_pic.png",
        "pic_recs": "http://mycompany.com/rec_pic.jpg",
        "region": "string",
        "team_ids": [
            "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        ],
        "gp_project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "gp_company_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "gp_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "comments": "string",

    }


@pytest.fixture()
def vacancy_skill():
    return {
        "skill_id": "46c1b999-4d9f-40b2-92a2-59a51fc9571b",
        "is_competence": True,
        "skill_description": "string",
        "desirability": "REQUIRED",
        "level": "EXPERT",
        "priority": 1,
    }


@pytest.fixture()
def empty_vacancy_with_skills(empty_vacancy, vacancy_skill):
    vacancy = empty_vacancy.copy()
    vacancy["skills"] = [vacancy_skill]
    vacancy["skills"].append(
        {
            "skill_id": "46c1b999-2a8c-40b2-92a2-59a51fc9571b",
            "is_competence": False,
            "skill_description": "string",
            "desirability": "DESIRED",
            "level": "JUNIOR",
            "priority": 1,
        }
    )
    return vacancy


@pytest.fixture()
def vacancy_response_full():
    return {"gp_project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "gp_company_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "gp_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "vacancy_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "data_response": [
                {
                    "first_name": "string",
                    "last_name": "string",
                    "middle_name": "string",
                    "email": "user@example.com",
                    "phone": "87123456789",
                    "city": "string",
                    "best_season": "string",
                    "best_status": "string"
                }
            ],
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }




import asyncio
import json
from typing import Union, Dict, List

import httpx

from app.schemas.vacancy_notify import PostTelegramVacancy
from app.schemas.vacancy import Contact, Requirements, Conditions

from app.core import config


def list_of_params_to_dict(list_: List[Union[Contact, Requirements, Conditions]]) -> Dict:
    """
    Function transform list of Contact/Requirements/Conditions objects to dictionary
    and then transit it to SiNoRa service.
    """
    result = {}
    for elem in list_:
        if isinstance(elem, Contact):
            result[elem.type] = elem.contact
        elif isinstance(elem, Requirements):
            result[elem.experience] = elem.description
        elif isinstance(elem, Conditions):
            condition = []
            if elem.schedule:
                condition.append(elem.schedule)
            if elem.employment:
                condition.append(elem.employment)
            if elem.other:
                condition.append(elem.other)
            result["condition_" + str(list_.index(elem))] = ", ".join(condition)
    return result


async def post_to_telegram(vacancy_post: PostTelegramVacancy) -> Dict:
    """
    Function send post of vacancy to SiNoRa service, which send message to Telegram's chanelle.
    """
    params = [config.settings.URL_SINORA_NOTIFICATION,
              config.settings.USER_UUID,
              config.settings.PROJECT_UUID,
              config.settings.TEMPLATE_UUID,
              config.settings.EVENT_CODE_NAME,
              config.settings.TELEGRAM_CHANNEL_ID_CLOVERI,
              ]
    if not all(params):
        return {"status_code": 503}

    async with httpx.AsyncClient() as client:
        url = config.settings.URL_SINORA_NOTIFICATION
        headers = {
            "Content-Type": "application/json"
        }
        body = {
          "event_code": config.settings.EVENT_CODE_NAME,
          "user_identifier": config.settings.USER_UUID,
          "project_identifier": config.settings.PROJECT_UUID,
          "message_recipients": [
            {
                'telegram_chat_id': config.settings.TELEGRAM_CHANNEL_ID_CLOVERI,
             }
          ],
          "parameters": {
              "c_name": vacancy_post.name,
              "c_company_name": vacancy_post.company_name,
              "c_full_description": vacancy_post.full_description,
              "c_contacts": list_of_params_to_dict(vacancy_post.contacts),
              "c_requirements": list_of_params_to_dict(vacancy_post.requirements),
              "c_conditions": list_of_params_to_dict(vacancy_post.conditions),
              "c_responsibilities": vacancy_post.responsibilities,
          }
        }
        response = await client.post(url, headers=headers, json=body)
        result = response.json()
        result_dict = json.loads(result)
        result_dict["status_code"] = response.status_code
    return result_dict

if __name__ == '__main__':
    def vacancy_skill():
        return {
            "skill_id": "46c1b999-4d9f-40b2-92a2-59a51fc9571b",
            "is_competence": True,
            "skill_description": "string",
            "desirability": "REQUIRED",
            "level": "EXPERT",
            "priority": 1,
        }

    def full_vacancy():
        return {
            "name": "BackEnd Developer",
            "is_active": False,
            "company_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "company_name": "Cloveri Test",
            "positions": 0,
            "requirements": [
                {
                    "experience": "Python",
                    "description": "Should be Senior"
                },
                {
                    "experience": "JavaScript",
                    "description": "Should be Junior"
                }
            ],
            "conditions": [
                {
                    "schedule": "5x8",
                    "employment": "full time",
                    "other": "in office"
                },
                {
                    "schedule": "5x4",
                    "employment": "part time",
                    "other": "remote mode"
                },
            ],
            "responsibilities": "Result of development interesting application",
            "short_description": "string",
            "full_description": "Very fun and interesting work",
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
                },
                {
                    "type": "phone",
                    "contact": "1234567890"
                },
                {
                    "type": "telegram",
                    "contact": "@accounttelegram"
                },
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

    test_vacancy_post_dict = full_vacancy()
    test_vacancy_post_dict["skills"] = [vacancy_skill()]
    test_vacancy_post = PostTelegramVacancy(**test_vacancy_post_dict)

    def sync_result():
        return asyncio.run(post_to_telegram(test_vacancy_post))

    print('Result from SiNoRa: ', sync_result())

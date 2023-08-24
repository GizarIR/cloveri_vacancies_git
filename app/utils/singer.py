import asyncio
import base64
import datetime
import hashlib
import hmac
from typing import Optional, Union
from uuid import UUID
import secrets

import httpx

from app.api.message_manager import MessageManager
from starlette.responses import JSONResponse

from app.core import config

# This is  dict for save api_token as cache
TOKEN_PROJECT_MAPPING = {
    # "gp_project_id1": "API_TOKEN1",
}

TIME_LIMIT = 180

# Encoder json to str - need for Case 2
def json_2_str(json_obj):
    schema_bytes = str(json_obj).encode('utf-8')
    encoded = base64.b64encode(schema_bytes)
    return encoded.decode('utf-8')


def create_sign(key: str, message):
    """
    Function generate signature for message using key and algorithm sha1
    """
    key = key.encode()
    message = message.encode()
    signing = hmac.new(key, message, hashlib.sha256)
    return signing.hexdigest()


async def check_gp_project_id(gp_project_id: UUID) -> Optional[Union[bool, str]]:
    """
    Check gp_project_id in local dict, request API token from Registry service.
    Return api token or False
    """

    if str(gp_project_id) not in TOKEN_PROJECT_MAPPING:

        if config.settings.URL_REGISTRY_SERVICE:
            url_registry = config.settings.URL_REGISTRY_SERVICE
        else:
            return False

        async with httpx.AsyncClient() as client:
            url = url_registry + str(gp_project_id)
            headers = {
                "Content-Type": "application/json"
            }
            response = await client.get(url, headers=headers)

            # Handle response Registry service
            if response.status_code == 200:
                data = response.json()
                if len(data['results']):
                    dict_record_registry = data['results'][0]
                    api_token = dict_record_registry.get('object_code', {})
                    TOKEN_PROJECT_MAPPING[str(gp_project_id)] = api_token
                else:
                    return False
                return api_token
            else:
                return False
    else:
        return TOKEN_PROJECT_MAPPING[str(gp_project_id)]


def check_signs(received_signature: str,
                project_id: UUID,
                api_token: str,
                data_fields: Optional[str] = "",
                items_id: Optional[str] = "",
                time: Optional[str] = "") -> bool:
    """
    Function are checking signature
    *received_signature* - signature
    *gp_project_id* - UUID id project from group of company's
    *data_fields* - str of parameters from the query obtained by concatenating parameters into a single str
    *items_id*  - str of parameters from the path obtained by concatenating parameters into a single str
    """
    # message = str(gp_project_id) + data_fields + items_id + time
    message = ""
    list_message =[]
    # Sort dict for original name key from endpoint
    if project_id:
        list_message.append(str(project_id))
    if data_fields:
        list_message.append(str(data_fields)) # original name from endpoint - service
    if items_id:
        list_message.append(str(items_id))
    if time:
        list_message.append(str(time))
    if config.settings.SECRET_KEY:
        list_message.append(config.settings.SECRET_KEY)
    message = ":".join(list_message)
    print("MESSAGE: ", message)
    signature = create_sign(api_token, message)
    return hmac.compare_digest(received_signature, signature)


async def check_authority(gp_project_id: UUID,
                          received_signature: str,
                          data_fields: Optional[str] = "",
                          items_id: Optional[str] = "",
                          time: Optional[str] = "") -> Optional[Union[None, JSONResponse]]:
    """
    Function check authority operations
    """

    if time and (datetime.datetime.now().timestamp() - float(time)) > TIME_LIMIT:
        return JSONResponse(
            status_code=419, content=MessageManager.timeout_signature()
        )

    api_token = await check_gp_project_id(gp_project_id)

    if not api_token:
        return JSONResponse(
            status_code=404,
            content=MessageManager.get_gp_project_id_nothing_found_msg_or_unavailable_registry(gp_project_id)
        )
    else:
        if not check_signs(received_signature, gp_project_id, api_token, data_fields=data_fields, items_id=items_id, time=time):
            if config.settings.SINGER_DEBUG:
                print(check_signs(received_signature, gp_project_id, api_token, data_fields=data_fields, items_id=items_id, time=time))
                print('RETURN gp_project_id: ', gp_project_id)
                print(f'RETURN STR data_field: {data_fields}')
                print(f'RETURN STR items_id: {items_id}')
                print(f'RETURN STR time: {time}')
                print(f'RETURN STR now timestamp: {datetime.datetime.now().timestamp()}')
                sign_status = 'API_TOKEN not found'
                list_message_suggest = []
                message_suggest = ""
                if api_token:
                    # Sort dict for original name key from endpoint
                    if gp_project_id:
                        list_message_suggest.append(str(gp_project_id))
                    if data_fields:
                        list_message_suggest.append(str(data_fields))  # original name from endpoint - service
                    if items_id:
                        list_message_suggest.append(str(items_id))
                    if time:
                        list_message_suggest.append(str(time))
                    if config.settings.SECRET_KEY:
                        list_message_suggest.append(config.settings.SECRET_KEY)
                    message_suggest = ":".join(list_message_suggest)
                    sign_status = create_sign(str(api_token), message_suggest)
                print('Message: ', message_suggest)
                print('Sign: ', sign_status)

                returns = {
                    "Error": "Invalid signature",
                    "gp_project_id": f'{gp_project_id}',
                    "str_data_field": f'{data_fields}',
                    "str_items_id": f"{items_id}",
                    "time_from_data": f"{time}",
                    "now timestamp": f"{datetime.datetime.now().timestamp()}",
                    "message_saggest": f"{message_suggest}",
                    "Sign": sign_status
                }
                return JSONResponse(
                    status_code=401, content=returns
                )
            else:
                return JSONResponse(
                    status_code=401, content=MessageManager.invalid_signature()
                )
    return None


if __name__ == '__main__':
    test_gp_project_id = UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6')
    test_key = '84867699caf142072866faf2e75b7f6b'
    test_signature = '8ab931e8f2d2ebedbc64bffbca7c4a830ca76cb18679b744457bf8839e48af51'
    test_data_fields = 'vacancies'
    test_items_id = ''
    # test_time = '1690102109.828085'
    test_time = ''
    # not use items_id for test
    test_message = ":".join([str(test_gp_project_id), test_data_fields, test_time, config.settings.SECRET_KEY])
    print("TEST Message:" , test_message)
    signate_of_msg = create_sign(test_key, test_message)
    print('TEST create_sign: ', signate_of_msg)
    print('TEST check_signs: ', check_signs(
        test_signature, test_gp_project_id, test_key,
        test_data_fields, test_items_id, test_time))

    # Test connection to Registry service
    test_url_registry = config.settings.URL_REGISTRY_SERVICE

    def sync_result():
        return asyncio.run(check_gp_project_id(test_gp_project_id))

    print('If Service of Registry is available, you GOT TEST API-TOKEN: ', sync_result())
    print('NEW RANDOM API-TOKEN', secrets.token_hex(16))

import hmac
import pytest
from app.tests.test_signer3 import TOKEN_PROJECT_MAPPING
from app.utils.singer import check_authority, create_sign, check_signs
from uuid import UUID


def test_create_sign(mock_signature_procedure):
    key = "API_TOKEN"
    message = "test_message"
    signature = create_sign(key, message)

    assert isinstance(signature, str)
    assert len(signature) == 64


def test_check_signs():
    key = "test_key"
    signature = "cfab58132dad8a1b12a727ef085a812795068b093428eb842cc719b395d19e4c"
    gp_project_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    data_fields = "test_data_fields"
    items_id = "test_items_id"
    time = "test_time"

    assert check_signs(signature, gp_project_id, key, data_fields, items_id, time)


def test_check_signs_valid_signature(mock_signature_procedure):
    received_signature = "b40f827f5360739aba596bbec8f80eec2f2fab274274c5b7ee6d14923029b663"
    gp_project_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    data_fields = ""
    items_id = ""

    message = str(gp_project_id) + data_fields + items_id
    api_token = TOKEN_PROJECT_MAPPING.get(str(gp_project_id), "")
    signature = create_sign(api_token, message)
    assert hmac.compare_digest(signature, received_signature) is True


def test_check_signs_invalid_signature(mock_signature_procedure):
    received_signature = "0000000000000000000000000"
    gp_project_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    data_fields = ""
    items_id = ""

    message = str(gp_project_id) + data_fields + items_id
    api_token = TOKEN_PROJECT_MAPPING.get(str(gp_project_id), "")
    signature = create_sign(api_token, message)

    assert hmac.compare_digest(signature, received_signature) is False


@pytest.mark.asyncio
async def test_check_authority_invalid_gp_project_id(mock_signature_procedure):
    gp_project_id = UUID("3fa85f64-0000-0000-0000-2c963f66afa6")
    received_signature = "9f453065d07ddeb2aaed222e5f4f9f0000000000"
    data_fields = ""
    items_id = ""

    response = await check_authority(
        gp_project_id,
        received_signature,
        data_fields,
        items_id,
    )

    assert response is None or response.status_code == 404
    if response is not None:
        assert response.content == {
            "Error": "Invalid project ID",
            "gp_project_id": str(gp_project_id)
        }


@pytest.mark.asyncio
async def test_check_authority_invalid_signature(mock_signature_procedure):
    gp_project_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    received_signature = "invalid_signature"
    data_fields = ""
    items_id = ""

    response = await check_authority(
        gp_project_id,
        received_signature,
        data_fields,
        items_id,
    )
    assert response is None or response.status_code == 401
    if response is not None:
        assert response.content == {
            "Error": "Invalid signature",
            "gp_project_id": str(received_signature)
        }


@pytest.mark.asyncio
async def test_check_authority_valid_request(mock_signature_procedure):
    gp_project_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    received_signature = "9f453065d07ddeb2aaed222e5f4f9fc83b7d1d1c"
    data_fields = ""
    items_id = ""

    response = await check_authority(
        gp_project_id,
        received_signature,
        data_fields,
        items_id,
    )

    assert response is None

import base64
from typing import Any
from uuid import UUID
import datetime

from fastapi import APIRouter, Depends, Body
from fastapi.params import Query
from pydantic import EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api import deps
from app.api.message_manager import Message, MessageManager
from app.db.dal import DAL
from app.errors import VacancyNotFoundError
from app.schemas import vacancy as schemas
from app.schemas.vacancy_api import \
    SortingOrder, SortingParam, VacancyPage, \
    ResponseSortingParam, VacancyResponsePage, UserResponsePage
from app.schemas.vacancy_notify import PostTelegramVacancy
from app.schemas.auth import ServiceOperation

from app.utils.singer import check_authority, json_2_str, TIME_LIMIT
from app.utils.notifications import post_to_telegram

router = APIRouter()

EXAMPLE_UUID = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")


@router.post("/", response_model=schemas.Vacancy, status_code=201)
async def create_vacancy(
    vacancy_create: schemas.CreateVacancy,
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation  = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    session: AsyncSession = Depends(deps.get_session),
    request: Request = Body(..., embed=False)
) -> Any:
    """
    Creates new vacancy.
    """
    # Case 1
    # original_json = await request.json()
    # data_fields = str(original_json).lower().replace("'", '"').replace("none", "null").replace(" ", "")

    # Case 2
    # request: Request = Body(..., embed=False)
    # raw_body = await request.body()
    # # body_str = raw_body.decode("utf-8")
    # data_fields = json_2_str(raw_body)
    # print("RAW", data_fields)

    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    return await DAL(session).create_vacancy(vacancy_create)


@router.get(
    "/",
    response_model=VacancyPage,
    status_code=200,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {"example": MessageManager.get_nothing_found_msg()}
            },
        },
        400: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_invalid_filters_msg()
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def get_vacancies(
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation  = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    page: int = Query(0, ge=0, description="Page number"),
    limit: int = Query(50, ge=1, le=50, description="Page size limit"),
    gp_project_id: UUID = Query(None, description="Project filter"),
    company_id: UUID = Query(None, description="Company filter"),
    profession_id: UUID = Query(None, description="Profession filter"),
    team_id: UUID = Query(None, description="Team filter"),
    show_all: bool = Query(None, include_in_schema=False),
    sort_by: SortingParam = Query(SortingParam.none, description="Field to sort by"),
    sort_order: SortingOrder = Query(SortingOrder.asc),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieves a list of existing vacancies.
    """
    if not (profession_id or team_id or company_id or show_all):
        return JSONResponse(
            status_code=400, content=MessageManager.get_invalid_filters_msg()
        )

    # ***Check authority***
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***End check authority***

    result = await DAL(session).get_vacancies_page(
        page, limit, gp_project_id, company_id, profession_id, team_id, sort_by, sort_order
    )
    if result.items:
        return result
    return JSONResponse(status_code=404, content=MessageManager.get_nothing_found_msg())


@router.get(
    "/{vacancy_id}",
    response_model=schemas.Vacancy,
    status_code=200,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_vacancy_not_found_msg(EXAMPLE_UUID)
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def get_vacancy(
    vacancy_id: UUID,
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation  = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieves a vacancy by id.
    """
    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    result = await DAL(session).get_vacancy(vacancy_id)
    if result:
        return result
    return JSONResponse(
        status_code=404, content=MessageManager.get_vacancy_not_found_msg(vacancy_id)
    )


@router.put(
    "/{vacancy_id}",
    response_model=schemas.Vacancy,
    status_code=200,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_vacancy_not_found_msg(EXAMPLE_UUID)
                }
            },
        },
        400: {
            "model": Message,
            "content": {
                "application/json": {"example": MessageManager.get_ids_dont_match_msg()}
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def edit_vacancy(
    vacancy_id: UUID,
    vacancy_edit: schemas.EditVacancy,
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Edits a vacancy info by id.
    """
    if vacancy_id != vacancy_edit.id:
        return JSONResponse(
            status_code=400, content=MessageManager.get_ids_dont_match_msg()
        )

    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    result = await DAL(session).edit_vacancy(vacancy_edit)
    if result:
        return result
    return JSONResponse(
        status_code=404, content=MessageManager.get_vacancy_not_found_msg(vacancy_id)
    )


@router.delete(
    "/{vacancy_id}",
    status_code=200,
    response_model=Message,
    responses={
        200: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_successfully_deleted_msg(EXAMPLE_UUID)
                }
            },
        },
        404: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_vacancy_not_found_msg(EXAMPLE_UUID)
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def delete_vacancy(
    vacancy_id: UUID,
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieves a vacancy by id.
    """
    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    try:
        await DAL(session).delete_vacancy(vacancy_id)
        return JSONResponse(
            status_code=200,
            content=MessageManager.get_successfully_deleted_msg(vacancy_id),
        )
    except VacancyNotFoundError:
        return JSONResponse(
            status_code=404,
            content=MessageManager.get_vacancy_not_found_msg(vacancy_id),
        )


# Handle VacancyResponse
@router.get(
    "/{vacancy_id}/responses/",
    response_model=VacancyResponsePage,
    status_code=200,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {"example": MessageManager.get_nothing_responses_found_msg()}
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def get_vacancy_responses(
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    page: int = Query(0, ge=0, description="Page number"),
    limit: int = Query(50, ge=1, le=50, description="Page size limit"),
    vacancy_id: UUID = Query(None, description="Vacancy filter"),
    # show_all: bool = Query(None, include_in_schema=False),
    sort_by: ResponseSortingParam = Query(ResponseSortingParam.none, description="Field to sort by"),
    sort_order: SortingOrder = Query(SortingOrder.asc),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieves a list of existing vacancies.
    """

    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    result = await DAL(session).get_vacancy_responses_page(
        page, limit, vacancy_id, sort_by, sort_order
    )
    if result.items:
        return result
    return JSONResponse(status_code=404, content=MessageManager.get_nothing_responses_found_msg())


@router.post(
    "/responses/",
    response_model=schemas.VacancyResponse,
    status_code=201,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_vacancy_response_not_found_msg(EXAMPLE_UUID)
                }
            },
        },
        442: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_vacancy_response_not_found_msg(EXAMPLE_UUID)
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def create_vacancy_response(
    vacancy_response_create: schemas.CreateVacancyResponse,
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Creates new vacancy response.
    """
    # *** Prepare data for sign ***
    vacancy_data = await DAL(session).get_vacancy(vacancy_response_create.vacancy_id)
    if not vacancy_data:
        return JSONResponse(
            status_code=404, content=MessageManager.get_vacancy_not_found_msg(vacancy_response_create.vacancy_id)
        )
    # *** END Prepare data for sign ***

    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    try:
        return await DAL(session).create_vacancy_response(vacancy_response_create)
    except VacancyNotFoundError:
        return JSONResponse(
            status_code=404,
            content=MessageManager.get_vacancy_not_found_msg(vacancy_response_create.vacancy_id),
        )


@router.get(
    "/responses/{vacancy_response_id}",
    response_model=schemas.VacancyResponse,
    status_code=200,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_vacancy_response_not_found_msg(EXAMPLE_UUID)
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def get_vacancy_response(
    vacancy_response_id: UUID,
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieves a vacancy response by id.
    """

    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    result = await DAL(session).get_vacancy_response(vacancy_response_id)

    if result:
        return result
    return JSONResponse(
        status_code=404, content=MessageManager.get_vacancy_response_not_found_msg(vacancy_response_id)
    )


@router.get(
    "/responses/users/",
    response_model=VacancyResponsePage,
    status_code=200,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {"example": MessageManager.get_user_responses_nothing_found_msg()}
            },
        },
        400: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_invalid_filters_user_response_msg()
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def get_user_responses(
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    page: int = Query(0, ge=0, description="Page number"),
    limit: int = Query(50, ge=1, le=50, description="Page size limit"),
    gp_user_id: UUID = Query(None, description="User filter"),
    first_name: str = Query(None, description="First name"),
    last_name: str = Query(None, description="Last name"),
    middle_name: str = Query(None, description="Middle name"),
    email: EmailStr = Query(None, description="Email filter"),
    phone: str = Query(None, description="Phone number filter"),
    show_all: bool = Query(None, include_in_schema=False),
    sort_by: ResponseSortingParam = Query(ResponseSortingParam.none, description="Field to sort by"),
    sort_order: SortingOrder = Query(SortingOrder.asc),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieves a list of existing user's responses.
    """

    if not any([gp_user_id, first_name, last_name, middle_name, email, phone, show_all]):
        return JSONResponse(
            status_code=400, content=MessageManager.get_invalid_filters_user_response_msg()
        )
    # ***** Check authority ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    result = await DAL(session).get_user_responses_page(
        page, limit, gp_user_id, first_name, last_name, middle_name, email, phone, sort_by, sort_order
    )
    if result.items:
        return result
    return JSONResponse(status_code=404, content=MessageManager.get_user_responses_nothing_found_msg())


@router.get(
    "/v2/responses/users/",
    response_model=UserResponsePage,
    status_code=200,
    responses={
        404: {
            "model": Message,
            "content": {
                "application/json": {"example": MessageManager.get_user_responses_nothing_found_msg()}
            },
        },
        400: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_invalid_filters_user_response_msg()
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
    },
)
async def v2_get_user_responses(
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    page: int = Query(0, ge=0, description="Page number"),
    limit: int = Query(50, ge=1, le=50, description="Page size limit"),
    gp_user_id: UUID = Query(None, description="User filter"),
    first_name: str = Query(None, description="First name"),
    last_name: str = Query(None, description="Last name"),
    middle_name: str = Query(None, description="Middle name"),
    email: EmailStr = Query(None, description="Email filter"),
    phone: str = Query(None, description="Phone number filter"),
    show_all: bool = Query(None, include_in_schema=False),
    sort_by: ResponseSortingParam = Query(ResponseSortingParam.none, description="Field to sort by"),
    sort_order: SortingOrder = Query(SortingOrder.asc),
    session: AsyncSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieves a list of existing user's responses in one list.
    """
    if not (gp_user_id or first_name or last_name or middle_name or email or phone or show_all):
        return JSONResponse(
            status_code=400, content=MessageManager.get_invalid_filters_user_response_msg()
        )

    # ***Check authority***
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***End check authority***

    result = await DAL(session).v2_get_user_responses_page(
        page, limit, gp_user_id, first_name, last_name, middle_name, email, phone, sort_by, sort_order
    )

    if result.items:
        return result
    return JSONResponse(status_code=404, content=MessageManager.get_user_responses_nothing_found_msg())


@router.post(
    "/notify/{vacancy_id}",
    response_model=Message,
    status_code=200,
    responses={
        200: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_successfully_notify_msg(EXAMPLE_UUID)
                }
            },
        },
        419: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.timeout_signature()
                }
            },
        },
        422: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_service_validation_error("SiNoRa", {'detail': 'string'})
                }
            },
        },
        503: {
            "model": Message,
            "content": {
                "application/json": {
                    "example": MessageManager.get_service_unavailable_msg("SiNoRa")
                }
            },
        },
    },
)
async def post_vacancy_to_telegram(
    vacancy_id: UUID,
    vacancy_post: PostTelegramVacancy,
    project_id: UUID = Query(..., description="Project ID of service"),
    service: ServiceOperation = Query(..., description="Type of operation"),
    time: str = Query("", description="Timestamp, format is unix time"),
    signature: str = Query("", description="Signature of data"),
    # session: AsyncSession = Depends(deps.get_session),
    # request: Request = Body(..., embed=False)
) -> Any:
    """
    Posting vacancy to Telegram channel using service SiNoRa.
    """

    # ***** Check authority Case 1 ******
    authority_error = await check_authority(project_id, signature, data_fields=str(service.value), time=time)

    if authority_error:
        return authority_error
    # ***** End Check authority ******

    # *** Posting vacancy to Telegram ***
    response = await post_to_telegram(vacancy_post)
    if response["status_code"] == 200:
        return JSONResponse(
            status_code=200,
            content=MessageManager.get_successfully_notify_msg(vacancy_id),
        )
    elif response["status_code"] == 422:
        return JSONResponse(
            status_code=422,
            content=MessageManager.get_service_validation_error("SiNoRa", response),
        )
    else:
        return JSONResponse(
            status_code=503,
            content=MessageManager.get_service_unavailable_msg("SiNoRa"),
        )
    # *** END Posting vacancy to Telegram ***

# @router.put("/me", response_model=schemas.User)
# async def update_user_me(
#     user_update: schemas.UserUpdate,
#     session: AsyncSession = Depends(deps.get_session),
#     current_user: models.User = Depends(deps.get_current_user),
# ):
#     """
#     Update current user.
#     """
#     if user_update.password is not None:
#         current_user.hashed_password = get_password_hash(user_update.password)  # type: ignore  #noqa
#     if user_update.full_name is not None:
#         current_user.full_name = user_update.full_name  # type: ignore
#     if user_update.email is not None:
#         current_user.email = user_update.email  # type: ignore
#
#     session.add(current_user)
#     await session.commit()
#     await session.refresh(current_user)
#
#     return current_user
#
#
# @router.get("/me", response_model=schemas.User)
# async def read_user_me(
#     current_user: models.User = Depends(deps.get_current_user),
# ):
#     """
#     Get current user.
#     """
#     return current_user

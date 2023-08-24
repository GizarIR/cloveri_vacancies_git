from fastapi import APIRouter

from app.api.endpoints import vacancies

api_router = APIRouter()
api_router.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])

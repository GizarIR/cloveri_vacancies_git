"""
Main FastAPI app instance declaration
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core import config

app = FastAPI(
    title=config.settings.PROJECT_NAME,
    version=config.settings.VERSION,
    description=config.settings.DESCRIPTION,
    openapi_url="/openapi.json",
    docs_url="/",
)


# Set all CORS enabled origins
if config.settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

if __name__ == "__main__":
    if config.settings.ENVIRONMENT == "STAGE":
        uvicorn.run("app.main:app", host="api.elbrus.skroy.ru", port=8001, reload=True, access_log=False)
    else:
        uvicorn.run("app.main:app", port=5001, reload=True, access_log=False)

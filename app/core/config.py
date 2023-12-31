"""
File with environment variables and general configuration logic.
`SECRET_KEY`, `ENVIRONMENT` etc. map to env variables with the same names.

Pydantic priority ordering:

1. (Most important, will overwrite everything) - environment variables
2. `.env` file in root folder of project
3. Default values

For project name, version, description we use pyproject.toml
For the rest, we use file `.env` (gitignored), see `.env.example`

`DEFAULT_SQLALCHEMY_DATABASE_URI` and `TEST_SQLALCHEMY_DATABASE_URI`:
Both are ment to be validated at the runtime, do not change unless you know
what are you doing. All the two validators do is to build full URI (TCP protocol)
to databases to avoid typo bugs.

See https://pydantic-docs.helpmanual.io/usage/settings/
"""

from pathlib import Path
from typing import Literal, Union

import toml
from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, validator

PROJECT_DIR = Path(__file__).parent.parent.parent
PYPROJECT_CONTENT = toml.load(f"{PROJECT_DIR}/pyproject.toml")["tool"]["poetry"]


class Settings(BaseSettings):
    # CORE SETTINGS
    SECRET_KEY: str
    ENVIRONMENT: Literal["DEV", "PYTEST", "STAGE", "PRODUCTION"]
    BACKEND_CORS_ORIGINS: Union[str, list[AnyHttpUrl]]

    # PROJECT NAME, VERSION AND DESCRIPTION
    PROJECT_NAME: str = PYPROJECT_CONTENT["name"]
    VERSION: str = PYPROJECT_CONTENT["version"]
    DESCRIPTION: str = PYPROJECT_CONTENT["description"]

    # POSTGRESQL DEFAULT DATABASE
    DEFAULT_DATABASE_HOSTNAME: str
    DEFAULT_DATABASE_USER: str
    DEFAULT_DATABASE_PASSWORD: str
    DEFAULT_DATABASE_PORT: str
    DEFAULT_DATABASE_DB: str
    DEFAULT_SQLALCHEMY_DATABASE_URI: str = ""

    # POSTGRESQL TEST DATABASE
    TEST_DATABASE_HOSTNAME: str
    TEST_DATABASE_USER: str
    TEST_DATABASE_PASSWORD: str
    TEST_DATABASE_PORT: str
    TEST_DATABASE_DB: str
    TEST_SQLALCHEMY_DATABASE_URI: str = ""

    # POSTGRESQL STAGE DATABASE
    STAGE_DATABASE_HOSTNAME: str
    STAGE_DATABASE_USER: str
    STAGE_DATABASE_PASSWORD: str
    STAGE_DATABASE_PORT: str
    STAGE_DATABASE_DB: str
    STAGE_SQLALCHEMY_DATABASE_URI: str = ""
    
    # POSTGRESQL PRODUCTION DATABASE
    PRODUCTION_DATABASE_HOSTNAME: str
    PRODUCTION_DATABASE_USER: str
    PRODUCTION_DATABASE_PASSWORD: str
    PRODUCTION_DATABASE_PORT: str
    PRODUCTION_DATABASE_DB: str
    PRODUCTION_SQLALCHEMY_DATABASE_URI: str = ""

    #  Registry service
    URL_REGISTRY_SERVICE: str = ""
    SINGER_DEBUG: bool = False

    # SiNoRa notification's service
    URL_SINORA_NOTIFICATION: str = ""
    USER_UUID: str = ""
    PROJECT_UUID: str = ""
    TEMPLATE_UUID: str = ""
    EVENT_CODE_NAME: str = ""
    TELEGRAM_CHANNEL_ID_CLOVERI: int = 0

    # VALIDATORS
    @validator("BACKEND_CORS_ORIGINS")
    def _assemble_cors_origins(cls, cors_origins: Union[str, list[AnyHttpUrl]]):
        if isinstance(cors_origins, str):
            return [item.strip() for item in cors_origins.split(",")]
        return cors_origins

    @validator("DEFAULT_SQLALCHEMY_DATABASE_URI")
    def _assemble_default_db_connection(cls, v: str, values: dict[str, str]) -> str:
        return AnyUrl.build(
            scheme="postgresql+asyncpg",
            user=values["DEFAULT_DATABASE_USER"],
            password=values["DEFAULT_DATABASE_PASSWORD"],
            host=values["DEFAULT_DATABASE_HOSTNAME"],
            port=values["DEFAULT_DATABASE_PORT"],
            path=f"/{values['DEFAULT_DATABASE_DB']}",
        )

    @validator("TEST_SQLALCHEMY_DATABASE_URI")
    def _assemble_test_db_connection(cls, v: str, values: dict[str, str]) -> str:
        return AnyUrl.build(
            scheme="postgresql+asyncpg",
            user=values["TEST_DATABASE_USER"],
            password=values["TEST_DATABASE_PASSWORD"],
            host=values["TEST_DATABASE_HOSTNAME"],
            port=values["TEST_DATABASE_PORT"],
            path=f"/{values['TEST_DATABASE_DB']}",
        )

    @validator("STAGE_SQLALCHEMY_DATABASE_URI")
    def _assemble_stage_db_connection(cls, v: str, values: dict[str, str]) -> str:
        return AnyUrl.build(
            scheme="postgresql+asyncpg",
            user=values["STAGE_DATABASE_USER"],
            password=values["STAGE_DATABASE_PASSWORD"],
            host=values["STAGE_DATABASE_HOSTNAME"],
            port=values["STAGE_DATABASE_PORT"],
            path=f"/{values['STAGE_DATABASE_DB']}",
        )

    @validator("PRODUCTION_SQLALCHEMY_DATABASE_URI")
    def _assemble_production_db_connection(cls, v: str, values: dict[str, str]) -> str:
        return AnyUrl.build(
            scheme="postgresql+asyncpg",
            user=values["PRODUCTION_DATABASE_USER"],
            password=values["PRODUCTION_DATABASE_PASSWORD"],
            host=values["PRODUCTION_DATABASE_HOSTNAME"],
            port=values["PRODUCTION_DATABASE_PORT"],
            path=f"/{values['PRODUCTION_DATABASE_DB']}",
        )

    def get_database_uri(self):
        if self.ENVIRONMENT == "DEV":
            return self.DEFAULT_SQLALCHEMY_DATABASE_URI
        elif self.ENVIRONMENT == "PYTEST":
            return self.TEST_SQLALCHEMY_DATABASE_URI
        elif self.ENVIRONMENT == "STAGE":
            return self.STAGE_SQLALCHEMY_DATABASE_URI
        elif self.ENVIRONMENT == "PRODUCTION":
            return self.PRODUCTION_SQLALCHEMY_DATABASE_URI
        else:
            raise("Specified ENVIRONMENT %s is not associated with any DBs".format(self.ENVIRONMENT))


    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings: Settings = Settings()  # type: ignore

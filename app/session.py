import json
from functools import partial

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from app.core import config

sqlalchemy_database_uri = config.settings.get_database_uri()

async_engine = create_async_engine(
    sqlalchemy_database_uri,
    json_serializer=partial(json.dumps, ensure_ascii=False),
    pool_pre_ping=True
)

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

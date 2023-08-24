import asyncio
from typing import AsyncGenerator
from unittest.mock import patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config
from app.db.models import Base
from app.main import app
from app.session import async_engine, async_session
from .fixtures import *  # noqa


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture()
def clean_db_on_setup(event_loop):
    event_loop.run_until_complete(test_db_setup())
    yield


@pytest.fixture()
def clean_db_on_teardown(event_loop):
    yield
    event_loop.run_until_complete(test_db_setup())


async def test_db_setup():
    # assert if we use TEST_DB URL for 100%
    assert config.settings.ENVIRONMENT == "PYTEST"
    assert str(async_engine.url) == config.settings.TEST_SQLALCHEMY_DATABASE_URI

    # always drop and create test db tables between tests session
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return async_session


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True, scope="session")
def alembic_migrate(event_loop):
    event_loop.run_until_complete(test_db_setup())


# @pytest.fixture
# async def default_user(session: AsyncSession):
#     result = await session.execute(select(User).where(User.email == default_user_email))
#     user: Optional[User] = result.scalars().first()
#     if user is None:
#         new_user = User(
#             email=default_user_email,
#             hashed_password=default_user_hash,
#             full_name="fullname",
#         )
#         session.add(new_user)
#         await session.commit()
#         await session.refresh(new_user)
#         return new_user
#     return user

@pytest.fixture
def mock_check_gp_project_id():
    with patch("app.utils.singer.check_gp_project_id", return_value=True) as patch_check_gp_project_id:
        yield patch_check_gp_project_id


@pytest.fixture
def mock_check_signs():
    with patch("app.utils.singer.check_signs", return_value=True) as patch_check_signs:
        yield patch_check_signs


@pytest.fixture
def mock_signature_procedure(mock_check_gp_project_id, mock_check_signs):
    yield mock_check_gp_project_id, mock_check_signs

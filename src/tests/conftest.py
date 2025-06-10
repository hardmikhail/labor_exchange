import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from dependency_injector import providers
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import DBSettings
from config.common import TestIds
from main import app
from repositories import UserRepository
from repositories.job_repository import JobRepository
from repositories.response_repository import ResponseRepository
from tools.fixtures.jobs import JobFactory
from tools.fixtures.responses import ResponseFactory
from tools.fixtures.users import UserFactory
from tools.security import create_access_token
from web.schemas.auth import TokenSchema

env_file_name = ".env." + os.environ.get("STAGE", "test")
env_file_path = Path(__file__).parent.parent.resolve() / env_file_name
settings = DBSettings(_env_file=env_file_path)


@pytest_asyncio.fixture()
async def access_token(test_user):
    token = TokenSchema(
        access_token=create_access_token(
            {"sub": str(test_user.id), "is_company": test_user.is_company}
        ),
        token_type="Bearer",
    )
    return token


@pytest_asyncio.fixture()
async def access_token_comp(test_company):
    token = TokenSchema(
        access_token=create_access_token(
            {"sub": str(test_company.id), "is_company": test_company.is_company}
        ),
        token_type="Bearer",
    )
    return token


@pytest_asyncio.fixture()
async def app_with_di():
    yield app


@pytest_asyncio.fixture()
async def client_with_fake_db(app_with_di, access_token, sa_session):
    app_with_di.container.repositories_container.job_repository.override(
        providers.Factory(JobRepository, session=sa_session)
    )

    app_with_di.container.repositories_container.user_repository.override(
        providers.Factory(UserRepository, session=sa_session)
    )

    app_with_di.container.repositories_container.response_repository.override(
        providers.Factory(ResponseRepository, session=sa_session)
    )

    async with AsyncClient(app=app_with_di, base_url="http://test") as client:
        client.headers["Authorization"] = f"Bearer {access_token.access_token}"
        yield client


@pytest.fixture()
def client_app():
    client = TestClient(app)
    return client


@pytest_asyncio.fixture(scope="function")
async def sa_session():
    engine = create_async_engine(str(settings.pg_async_dsn))
    connection = await engine.connect()
    trans = await connection.begin()

    Session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)  # noqa
    session = Session()

    deletion = session.delete

    async def mock_delete(instance):
        insp = inspect(instance)
        if not insp.persistent:
            session.expunge(instance)
        else:
            await deletion(instance)

        return await asyncio.sleep(0)

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    @asynccontextmanager
    async def db():
        yield session

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    try:
        yield db
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def user_repository(sa_session):
    repository = UserRepository(session=sa_session)
    yield repository


@pytest_asyncio.fixture(scope="function")
async def job_repository(sa_session):
    repository = JobRepository(session=sa_session)
    yield repository


@pytest_asyncio.fixture(scope="function")
async def response_repository(sa_session):
    repository = ResponseRepository(session=sa_session)
    yield repository


@pytest_asyncio.fixture(scope="function", autouse=True)
def setup_factories(sa_session: AsyncSession) -> None:
    UserFactory.session = sa_session
    JobFactory.session = sa_session


@pytest_asyncio.fixture(scope="function")
async def test_user(sa_session):
    async with sa_session() as session:
        user = UserFactory.build(id=TestIds.USER, is_company=False)
        session.add(user)
        await session.flush()

        yield user


@pytest_asyncio.fixture(scope="function")
async def test_company(sa_session):
    async with sa_session() as session:
        company = UserFactory.build(id=TestIds.COMPANY, is_company=True)
        session.add(company)
        await session.flush()

        yield company


@pytest_asyncio.fixture(scope="function")
async def test_job(sa_session, test_company):
    async with sa_session() as session:
        job = JobFactory.build(id=TestIds.JOB, user_id=TestIds.COMPANY)
        session.add(job)
        await session.flush()

        yield job


@pytest_asyncio.fixture(scope="function")
async def test_response(sa_session, test_user, test_job):
    async with sa_session() as session:
        response = ResponseFactory.build(
            id=TestIds.RESPONSE, user_id=TestIds.USER, job_id=TestIds.JOB
        )
        session.add(response)
        await session.flush()

        yield response

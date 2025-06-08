import http

import pytest
from httpx import AsyncClient

from tools.common import fake
from tools.fixtures.users import UserFactory


@pytest.mark.asyncio
async def test_read_users(client_with_fake_db, sa_session):
    async with sa_session() as session:
        count_of_users = 3
        users = [UserFactory.build() for _ in range(count_of_users)]
        [session.add(user) for user in users]
        await session.flush()

    response = await client_with_fake_db.get("/users")

    assert response.status_code == http.HTTPStatus.OK
    assert len(response.json()) == count_of_users + 1


@pytest.mark.asyncio
async def test_create_user(client_with_fake_db: AsyncClient):
    password = fake.password()

    json = {
        "name": fake.pystr(),
        "email": fake.email(),
        "password": password,
        "password2": password,
        "is_company": fake.pybool(),
    }

    response = await client_with_fake_db.post("/users", json=json)

    assert response.status_code == http.HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_read_user(client_with_fake_db: AsyncClient, test_user):
    response = await client_with_fake_db.get(f"/users/{test_user.id}")

    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_update_user(client_with_fake_db: AsyncClient, test_user):
    updated_name = fake.pystr()
    json = {
        "name": updated_name,
    }
    response = await client_with_fake_db.put(f"/users/{test_user.id}", json=json)

    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_user(client_with_fake_db: AsyncClient, test_user):
    response = await client_with_fake_db.delete(f"/users/{test_user.id}")

    assert response.status_code == http.HTTPStatus.NO_CONTENT

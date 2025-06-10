import http

import pytest
from httpx import AsyncClient

from tools.common import fake
from tools.fixtures.jobs import JobFactory


@pytest.mark.asyncio
async def test_create_job(client_with_fake_db: AsyncClient, test_company, access_token_comp):
    json = {
        "user_id": test_company.id,
        "title": fake.pystr(),
        "description": fake.text(),
        "salary_from": fake.pyfloat(positive=True, left_digits=3, right_digits=2, max_value=100),
        "salary_to": fake.pyfloat(positive=True, left_digits=3, right_digits=2, min_value=100),
        "is_active": fake.pybool(),
    }
    response = await client_with_fake_db.post(
        "/jobs",
        json=json,
        headers={
            "Authorization": f"{access_token_comp.token_type} {access_token_comp.access_token}"
        },
    )

    assert response.status_code == http.HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_read_jobs(client_with_fake_db: AsyncClient, sa_session, test_company):
    async with sa_session() as session:
        count_of_jobs = 5
        jobs = [JobFactory.build(user_id=test_company.id) for _ in range(count_of_jobs)]
        [session.add(job) for job in jobs]
        await session.flush()

    response = await client_with_fake_db.get("/jobs")

    assert response.status_code == http.HTTPStatus.OK
    assert len(response.json()) == count_of_jobs


@pytest.mark.asyncio
async def test_read_job(client_with_fake_db: AsyncClient, test_job):
    response = await client_with_fake_db.get(f"/jobs/{test_job.id}")

    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_update_job(client_with_fake_db: AsyncClient, test_job, access_token_comp):
    json = {"title": fake.pystr()}
    response = await client_with_fake_db.put(
        f"/jobs/{test_job.id}",
        json=json,
        headers={
            "Authorization": f"{access_token_comp.token_type} {access_token_comp.access_token}"
        },
    )

    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_job(client_with_fake_db: AsyncClient, test_job, access_token_comp):
    response = await client_with_fake_db.delete(
        f"/jobs/{test_job.id}",
        headers={
            "Authorization": f"{access_token_comp.token_type} {access_token_comp.access_token}"
        },
    )

    assert response.status_code == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_create_response(client_with_fake_db: AsyncClient, test_user, test_job):
    json = {
        "user_id": test_user.id,
        "job_id": test_job.id,
        "message": fake.text(),
    }
    response = await client_with_fake_db.post(f"/jobs/{test_job.id}/response", json=json)

    assert response.status_code == http.HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_get_responses_by_job_id(client_with_fake_db: AsyncClient, test_job):
    response = await client_with_fake_db.get(f"/jobs/{test_job.id}/responses")

    assert response.status_code == http.HTTPStatus.OK

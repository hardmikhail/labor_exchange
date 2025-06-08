import pytest
from pydantic import ValidationError

from repositories import JobRepository
from tools.fixtures.jobs import JobFactory
from tools.fixtures.responses import ResponseFactory
from tools.fixtures.users import UserFactory
from web.schemas import JobCreateSchema


@pytest.mark.asyncio
async def test_create_job(job_repository: JobRepository, user_repository, test_user):
    user = await user_repository.retrieve(id=1)
    job = JobCreateSchema(
        title="gpn",
        description="gpn",
        salary_from=1,
        salary_to=99999,
        is_active=True,
    )

    current_job = await job_repository.create(user_id=user.id, job_create_dto=job)

    assert current_job
    assert current_job.user_id == user.id
    assert current_job.title == job.title
    assert current_job.description == job.description
    assert current_job.salary_from == job.salary_from
    assert current_job.salary_to == job.salary_to
    assert current_job.is_active == job.is_active


@pytest.mark.asyncio
async def test_get_all(job_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        job = JobFactory.build(user_id=user.id)
        session.add(user)
        session.add(job)
        await session.flush()

    all_jobs = await job_repository.retrieve_many()

    assert all_jobs
    assert len(all_jobs) == 1

    job_from_repo = all_jobs[0]

    assert job_from_repo.id == job.id
    assert job_from_repo.user_id == job.user_id
    assert job_from_repo.title == job.title


@pytest.mark.asyncio
async def test_get_all_with_relations(job_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        job = JobFactory.build(user_id=user.id)
        response = ResponseFactory.build(user_id=user.id, job_id=job.id)
        session.add(user)
        session.add(job)
        session.add(response)
        await session.flush()

    all_jobs = await job_repository.retrieve_many(include_relations=True)

    assert all_jobs
    assert len(all_jobs) == 1

    job_from_repo = all_jobs[0]
    assert len(job_from_repo.responses) == 1
    assert job_from_repo.responses[0].id == response.id


@pytest.mark.asyncio
async def test_get_by_id(job_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        job = JobFactory.build(user_id=user.id)
        session.add(user)
        session.add(job)
        await session.flush()

    current_job = await job_repository.retrieve(id=job.id)
    assert current_job
    assert current_job.id == job.id


@pytest.mark.asyncio
async def test_create_with_invalid_data(job_repository):
    with pytest.raises(ValidationError):
        job = JobCreateSchema(
            title=129864,
            description="description",
            salary_from="100",
            salary_to="500",
            is_active=True,
        )

        await job_repository.create(job_create_dto=job, user_id=1)

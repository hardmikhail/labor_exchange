import pytest

from repositories.job_repository import JobRepository
from tools.fixtures.jobs import JobFactory
from tools.fixtures.users import UserFactory
from web.schemas.job import JobCreateSchema


@pytest.mark.asyncio
async def test_create_job(job_repository: JobRepository, user_repository, user_as_company):
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
        assert job_from_repo.description == job.description
        assert job_from_repo.salary_from == job.salary_from
        assert job_from_repo.salary_to == job.salary_to
        assert job_from_repo.is_active == job.is_active

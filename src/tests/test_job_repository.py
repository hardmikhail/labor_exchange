import pytest
from pydantic import ValidationError

from repositories import JobRepository
from tools.common import fake
from web.schemas import JobCreateSchema


@pytest.mark.asyncio
async def test_create_job(job_repository: JobRepository, test_user):
    job = JobCreateSchema(
        title=fake.pystr(),
        description=fake.text(),
        salary_from=fake.pyfloat(positive=True, left_digits=3, right_digits=2, max_value=100),
        salary_to=fake.pyfloat(positive=True, left_digits=3, right_digits=2, min_value=100),
        is_active=fake.pybool(),
    )

    current_job = await job_repository.create(user_id=test_user.id, job_create_dto=job)

    assert current_job
    assert current_job.user_id == test_user.id
    assert current_job.title == job.title
    assert current_job.description == job.description
    assert current_job.salary_from == job.salary_from
    assert current_job.salary_to == job.salary_to
    assert current_job.is_active == job.is_active


@pytest.mark.asyncio
async def test_get_all(job_repository, test_job):
    all_jobs = await job_repository.retrieve_many()

    assert all_jobs
    assert len(all_jobs) == 1

    job_from_repo = all_jobs[0]

    assert job_from_repo.id == test_job.id
    assert job_from_repo.user_id == test_job.user_id
    assert job_from_repo.title == test_job.title


@pytest.mark.asyncio
async def test_get_all_with_relations(job_repository, test_response):
    all_jobs = await job_repository.retrieve_many(include_relations=True)

    assert all_jobs
    assert len(all_jobs) == 1

    job_from_repo = all_jobs[0]

    assert len(job_from_repo.responses) == 1
    assert job_from_repo.responses[0].id == test_response.id


@pytest.mark.asyncio
async def test_get_by_id(job_repository, test_job):
    current_job = await job_repository.retrieve(id=test_job.id)

    assert current_job
    assert current_job.id == test_job.id


@pytest.mark.asyncio
async def test_create_with_invalid_data(job_repository, test_user):
    with pytest.raises(ValidationError):
        job = JobCreateSchema(
            title=fake.pybool(),
            description=fake.text(),
            salary_from=fake.pyfloat(left_digits=2, positive=False),
            salary_to=fake.pyfloat(left_digits=2),
            is_active=fake.pybool(),
        )

        await job_repository.create(job_create_dto=job, user_id=test_user.id)

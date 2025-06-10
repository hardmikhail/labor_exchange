import pytest
from pydantic import ValidationError

from repositories.response_repository import ResponseRepository
from tools.common import fake
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema


@pytest.mark.asyncio
async def test_create_response(response_repository: ResponseRepository, test_user, test_job):
    response = ResponseCreateSchema(
        message=fake.text(),
    )

    current_response = await response_repository.create(
        user_id=test_user.id, job_id=test_job.id, response_create_dto=response
    )

    assert current_response


@pytest.mark.asyncio
async def test_get_all(response_repository, test_response):

    all_responses = await response_repository.retrieve_many()

    assert all_responses
    assert len(all_responses) == 1

    response_from_repo = all_responses[0]

    assert response_from_repo.id == test_response.id
    assert response_from_repo.user_id == test_response.user_id
    assert response_from_repo.job_id == test_response.job_id
    assert response_from_repo.message == test_response.message


@pytest.mark.asyncio
async def test_get_by_id(response_repository, test_response):

    response = await response_repository.retrieve(id=test_response.id)

    assert response is not None
    assert response.id == test_response.id


@pytest.mark.asyncio
async def test_repository_raises_error_on_invalid_data(response_repository, test_user, test_job):
    with pytest.raises(ValidationError):
        response = ResponseCreateSchema(
            message=True,
        )

        await response_repository.create(
            user_id=test_user.id, job_id=test_job.id, response_create_dto=response
        )


@pytest.mark.asyncio
async def test_update(response_repository, test_response):
    updated_message = fake.text()

    response_update_dto = ResponseUpdateSchema(message=updated_message)
    updated_response = await response_repository.update(
        id=test_response.id, response_update_dto=response_update_dto
    )

    assert test_response.id == updated_response.id
    assert updated_response.message == updated_message


@pytest.mark.asyncio
async def test_delete(response_repository, test_response):
    await response_repository.delete(id=test_response.id, user_id=test_response.user_id)
    res = await response_repository.retrieve_many()

    assert not res

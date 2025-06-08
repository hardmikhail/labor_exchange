import pytest
from pydantic import ValidationError

from repositories.response_repository import ResponseRepository
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema


@pytest.mark.asyncio
async def test_create_response(
    response_repository: ResponseRepository, user_repository, job_repository, test_user, test_job
):
    user = await user_repository.retrieve(id=1)
    job = await job_repository.retrieve(id=1)
    response = ResponseCreateSchema(
        message="This is a test response",
    )

    current_response = await response_repository.create(
        user_id=user.id, job_id=job.id, response_create_dto=response
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


# @pytest.mark.asyncio
# async def test_get_all_with_relations(response_repository, sa_session):
#     async with sa_session() as session:
#         user = UserFactory.build(is_company=True)
#         job = JobFactory.build(user_id=user.id)
#         session.add(user)
#         session.add(job)
#         await session.flush()

#     all_users = await user_repository.retrieve_many(include_relations=True)
#     assert all_users
#     assert len(all_users) == 1

#     user_from_repo = all_users[0]
#     assert len(user_from_repo.jobs) == 1
#     assert user_from_repo.jobs[0].id == job.id
#     assert user_from_repo.id == user.id
#     assert user_from_repo.email == user.email
#     assert user_from_repo.name == user.name


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
    new_message = "new message"

    response_update_dto = ResponseUpdateSchema(message=new_message)
    updated_response = await response_repository.update(
        id=test_response.id, response_update_dto=response_update_dto
    )

    assert test_response.id == updated_response.id
    assert updated_response.message == new_message


@pytest.mark.asyncio
async def test_delete(response_repository, test_response):
    await response_repository.delete(id=test_response.id, user_id=test_response.user_id)
    res = await response_repository.retrieve_many()

    assert not res

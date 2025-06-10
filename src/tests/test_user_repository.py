import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from repositories.exceptions import UniqueError
from tools.common import fake
from tools.fixtures.users import UserFactory
from tools.security import hash_password
from web.schemas import UserCreateSchema, UserUpdateSchema


@pytest.mark.asyncio
async def test_get_all(user_repository, test_user):
    all_users = await user_repository.retrieve_many()
    assert all_users
    assert len(all_users) == 1

    user_from_repo = all_users[0]
    assert user_from_repo.id == test_user.id
    assert user_from_repo.email == test_user.email
    assert user_from_repo.name == test_user.name


@pytest.mark.asyncio
async def test_get_all_with_relations(user_repository, test_company, test_job):
    all_users = await user_repository.retrieve_many(include_relations=True)

    assert all_users
    assert len(all_users) == 1

    user_from_repo = all_users[0]
    assert len(user_from_repo.jobs) == 1
    assert user_from_repo.jobs[0].id == test_job.id
    assert user_from_repo.id == test_company.id
    assert user_from_repo.email == test_company.email
    assert user_from_repo.name == test_company.name


@pytest.mark.asyncio
async def test_get_by_id(user_repository, test_user):
    current_user = await user_repository.retrieve(id=test_user.id)

    assert current_user is not None
    assert current_user.id == test_user.id


@pytest.mark.asyncio
async def test_create_with_valid_data(user_repository):
    name = fake.pystr()
    password = fake.password()

    user = UserCreateSchema(
        name=name,
        email=fake.email(),
        password=password,
        password2=password,
        is_company=fake.pybool(),
    )

    new_user = await user_repository.create(
        user_create_dto=user, hashed_password=hash_password(user.password)
    )

    assert new_user is not None
    assert new_user.name == name
    assert new_user.hashed_password != password


@pytest.mark.asyncio
async def test_repository_raises_error_on_invalid_data(user_repository):
    name = fake.pystr()
    password = fake.password()

    with pytest.raises(ValidationError):
        user = UserCreateSchema(
            name=name,
            email=fake.email().replace("@", ""),
            password=password,
            password2=password,
            is_company=fake.pybool(),
        )

        await user_repository.create(
            user_create_dto=user, hashed_password=hash_password(user.password)
        )


@pytest.mark.asyncio
async def test_repository_rejects_duplicate_email(user_repository):
    name = fake.pystr()
    email = fake.email()
    password = fake.password()

    with pytest.raises(UniqueError):
        user = another_user = UserCreateSchema(
            name=name,
            email=email,
            password=password,
            password2=password,
            is_company=fake.pybool(),
        )

        await user_repository.create(
            user_create_dto=user, hashed_password=hash_password(user.password)
        )
        await user_repository.create(
            user_create_dto=another_user, hashed_password=hash_password(another_user.password)
        )


@pytest.mark.asyncio
async def test_create_password_mismatch(user_repository):
    name = fake.pystr()
    email = fake.email()

    with pytest.raises(ValidationError):
        user = UserCreateSchema(
            name=name,
            email=email,
            password=fake.password(),
            password2=fake.password(),
            is_company=fake.pybool(),
        )
        await user_repository.create(
            user_create_dto=user, hashed_password=hash_password(user.password)
        )


@pytest.mark.asyncio
async def test_update(user_repository, test_user):
    # async with sa_session() as session:
    #     user = UserFactory.build()
    #     session.add(user)
    #     await session.flush()

    updated_name = fake.pystr()
    user_update_dto = UserUpdateSchema(name=updated_name)
    updated_user = await user_repository.update(id=test_user.id, user_update_dto=user_update_dto)
    assert test_user.id == updated_user.id
    assert updated_user.name == updated_name


@pytest.mark.asyncio
async def test_update_email_from_other_user(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(email=fake.email())
        user2 = UserFactory.build()
        session.add(user)
        session.add(user2)
        await session.flush()

    user_update_dto = UserUpdateSchema(email=user.email)

    with pytest.raises(IntegrityError):
        await user_repository.update(id=user2.id, user_update_dto=user_update_dto)


@pytest.mark.asyncio
async def test_delete(user_repository, test_user):

    await user_repository.delete(id=test_user.id)
    res = await user_repository.retrieve_many()

    assert not res

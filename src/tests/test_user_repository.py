import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from repositories.exceptions import UniqueError
from tools.fixtures.jobs import JobFactory
from tools.fixtures.users import UserFactory
from tools.security import hash_password
from web.schemas import UserCreateSchema, UserUpdateSchema


@pytest.mark.asyncio
async def test_get_all(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        await session.flush()

    all_users = await user_repository.retrieve_many()
    assert all_users
    assert len(all_users) == 1

    user_from_repo = all_users[0]
    assert user_from_repo.id == user.id
    assert user_from_repo.email == user.email
    assert user_from_repo.name == user.name


@pytest.mark.asyncio
async def test_get_all_with_relations(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        job = JobFactory.build(user_id=user.id)
        session.add(user)
        session.add(job)
        await session.flush()

    all_users = await user_repository.retrieve_many(include_relations=True)
    assert all_users
    assert len(all_users) == 1

    user_from_repo = all_users[0]
    assert len(user_from_repo.jobs) == 1
    assert user_from_repo.jobs[0].id == job.id
    assert user_from_repo.id == user.id
    assert user_from_repo.email == user.email
    assert user_from_repo.name == user.name


@pytest.mark.asyncio
async def test_get_by_id(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        await session.flush()

    current_user = await user_repository.retrieve(id=user.id)
    assert current_user is not None
    assert current_user.id == user.id


@pytest.mark.asyncio
async def test_create_with_valid_data(user_repository):
    user = UserCreateSchema(
        name="Uchpochmak",
        email="bashkort@example.com",
        password="eshkere!",
        password2="eshkere!",
        is_company=False,
    )

    new_user = await user_repository.create(
        user_create_dto=user, hashed_password=hash_password(user.password)
    )
    assert new_user is not None
    assert new_user.name == "Uchpochmak"
    assert new_user.hashed_password != "eshkere!"


@pytest.mark.asyncio
async def test_repository_raises_error_on_invalid_data(user_repository):
    with pytest.raises(ValidationError):
        user = UserCreateSchema(
            name="Uchpochmak",
            email="wrong.email",
            password="eshkere!",
            password2="eshkere!",
            is_company=False,
        )

        await user_repository.create(
            user_create_dto=user, hashed_password=hash_password(user.password)
        )


@pytest.mark.asyncio
async def test_repository_rejects_duplicate_email(user_repository):
    with pytest.raises(UniqueError):
        user = UserCreateSchema(
            name="Uchpochmak",
            email="same@email.com",
            password="eshkere!",
            password2="eshkere!",
            is_company=False,
        )
        another_user = UserCreateSchema(
            name="Ochpochmak",
            email="same@email.com",
            password="eshkere!",
            password2="eshkere!",
            is_company=True,
        )

        await user_repository.create(
            user_create_dto=user, hashed_password=hash_password(user.password)
        )
        await user_repository.create(
            user_create_dto=another_user, hashed_password=hash_password(another_user.password)
        )


@pytest.mark.asyncio
async def test_create_password_mismatch(user_repository):
    with pytest.raises(ValidationError):
        user = UserCreateSchema(
            name="Uchpochmak",
            email="bashkort@example.com",
            password="eshkere!",
            password2="eshkero!",
            is_company=False,
        )
        await user_repository.create(
            user_create_dto=user, hashed_password=hash_password(user.password)
        )


@pytest.mark.asyncio
async def test_update(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        await session.flush()

    user_update_dto = UserUpdateSchema(name="updated_name")
    updated_user = await user_repository.update(id=user.id, user_update_dto=user_update_dto)
    assert user.id == updated_user.id
    assert updated_user.name == "updated_name"


@pytest.mark.asyncio
async def test_update_email_from_other_user(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(email="test@example.com")
        user2 = UserFactory.build()
        session.add(user)
        session.add(user2)
        await session.flush()

    user_update_dto = UserUpdateSchema(email=user.email)

    with pytest.raises(IntegrityError):
        await user_repository.update(id=user2.id, user_update_dto=user_update_dto)


@pytest.mark.asyncio
async def test_delete(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        await session.flush()

    await user_repository.delete(id=user.id)
    res = await user_repository.retrieve_many()
    assert not res

from interfaces.i_repository import IRepositoryAsync
from repositories.exceptions import EntityNotFoundError, UniqueError
from services.exception import UserAlreadyExistsError, UserNotFoundError
from tools.security import hash_password
from web.schemas import UserCreateSchema
from web.schemas.user import UserUpdateSchema


class UserService:
    def __init__(self, user_repository: IRepositoryAsync):
        self.user_repository = user_repository

    async def create(self, user_create_dto: UserCreateSchema):
        try:
            return await self.user_repository.create(
                user_create_dto, hashed_password=hash_password(user_create_dto.password)
            )
        except UniqueError as e:
            raise UserAlreadyExistsError("Пользователь уже существует в системе") from e

    async def retrieve(self, **kwargs):
        return await self.user_repository.retrieve(**kwargs)

    async def retrieve_many(self, limit: int, skip: int):
        return await self.user_repository.retrieve_many(limit=limit, skip=skip)

    async def update(self, id: int, user_update_dto: UserUpdateSchema):
        try:
            return await self.user_repository.update(id=id, user_update_dto=user_update_dto)
        except EntityNotFoundError as e:
            raise UserNotFoundError("Пользователь не найден") from e

    async def delete(self, id: int):
        try:
            return await self.user_repository.delete(id=id)
        except EntityNotFoundError as e:
            raise UserNotFoundError("Пользователь не найден") from e

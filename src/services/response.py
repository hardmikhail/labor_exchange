from interfaces.i_repository import IRepositoryAsync
from repositories.exceptions import EntityNotFoundError, UniqueError
from services.exception import (
    ResponseAlreadyExistsError,
    ResponseCreationError,
    ResponseNotFoundError,
)
from web.schemas import ResponseCreateSchema
from web.schemas.response import ResponseUpdateSchema


class ResponseService:
    def __init__(self, response_repository: IRepositoryAsync):
        self.response_repository = response_repository

    async def create(self, response_create_dto: ResponseCreateSchema):
        try:
            return await self.response_repository.create(response_create_dto)
        except UniqueError as e:
            raise ResponseAlreadyExistsError("Отклик уже существует в системе") from e
        except EntityNotFoundError as e:
            raise ResponseCreationError("Ошибка создания отклика") from e

    async def retrieve(self, **kwargs):
        try:
            return await self.response_repository.retrieve(**kwargs)
        except EntityNotFoundError as e:
            raise ResponseNotFoundError("Отклик не найден") from e

    async def retrieve_many(self, **kwargs):
        return await self.response_repository.retrieve_many(**kwargs)

    async def update(self, id: int, response_update_dto: ResponseUpdateSchema):
        try:
            return await self.response_repository.update(
                id=id, response_update_dto=response_update_dto
            )
        except EntityNotFoundError as e:
            raise ResponseNotFoundError("Отклик не найден") from e

    async def delete(self, id: int):
        try:
            return await self.response_repository.delete(id=id)
        except EntityNotFoundError as e:
            raise ResponseNotFoundError("Отклик не найден") from e

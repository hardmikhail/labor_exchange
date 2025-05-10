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

    async def create(
        self, user_id: int, job_id: int, is_company: bool, response_create_dto: ResponseCreateSchema
    ):
        if is_company:
            raise PermissionError("Недостаточно прав")
        try:
            return await self.response_repository.create(
                user_id=user_id, job_id=job_id, response_create_dto=response_create_dto
            )
        except UniqueError as e:
            raise ResponseAlreadyExistsError("Отклик уже существует в системе") from e
        except EntityNotFoundError as e:
            raise ResponseCreationError("Ошибка создания отклика") from e

    async def retrieve(self, user_id: int, **kwargs):
        try:
            response = await self.response_repository.retrieve(**kwargs)
            if response.user_id != user_id:
                raise PermissionError("Недостаточно прав")
            return response
        except EntityNotFoundError as e:
            raise ResponseNotFoundError("Отклик не найден") from e

    async def retrieve_many(self, **kwargs):
        return await self.response_repository.retrieve_many(**kwargs)

    async def update(self, id: int, user_id: int, response_update_dto: ResponseUpdateSchema):
        try:
            response = await self.response_repository.update(
                id=id,
                user_id=user_id,
                response_update_dto=response_update_dto,
            )
            if response.user_id != user_id:
                raise PermissionError("Недостаточно прав")
            return response
        except EntityNotFoundError as e:
            raise ResponseNotFoundError("Отклик не найден") from e

    async def delete(self, id: int, user_id: int):
        try:
            return await self.response_repository.delete(id=id, user_id=user_id)
        except EntityNotFoundError as e:
            raise ResponseNotFoundError("Отклик не найден") from e

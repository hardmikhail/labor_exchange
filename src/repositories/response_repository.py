from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from interfaces import IRepositoryAsync
from models import Response as ResponseModel
from repositories.exceptions import EntityNotFoundError, UniqueError
from storage.sqlalchemy.tables import Response
from tools.common import to_model, update_fields
from web.schemas import ResponseCreateSchema, ResponseUpdateSchema


class ResponseRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(
        self, user_id: int, job_id: int, response_create_dto: ResponseCreateSchema
    ) -> ResponseModel:
        try:
            async with self.session() as session:
                response = Response(
                    user_id=user_id,
                    job_id=job_id,
                    message=response_create_dto.message,
                )

                session.add(response)
                await session.commit()
                await session.refresh(response)

            return to_model(response, ResponseModel)
        except IntegrityError as e:
            if "violates foreign key constraint" in str(e).lower():
                raise EntityNotFoundError("Связанная запись не найдена") from e
            elif "violates unique constraint" in str(e).lower():
                raise UniqueError("Вы уже откликнулись на эту вакансию") from e
        except Exception:
            raise

    async def retrieve(self, **kwargs) -> ResponseModel:
        async with self.session() as session:
            query = select(Response).filter_by(**kwargs).limit(1)
            res = await session.execute(query)
            response_from_db = res.scalars().first()
            if not response_from_db:
                raise EntityNotFoundError("Отклик не найден")

        return to_model(response_from_db, ResponseModel)

    async def retrieve_many(self, limit: int = 100, skip: int = 0, **kwargs) -> list[ResponseModel]:
        async with self.session() as session:
            query = select(Response).limit(limit).offset(skip)
            res = await session.execute(query)
            response_from_db = res.scalars().all()

        responses_model = []
        for response in response_from_db:
            model = to_model(response, ResponseModel)
            responses_model.append(model)

        return responses_model

    async def update(
        self, id: int, user_id: int, response_update_dto: ResponseUpdateSchema
    ) -> ResponseModel:
        async with self.session() as session:
            query = select(Response).filter_by(id=id).limit(1)
            res = await session.execute(query)
            response_from_db = res.scalars().first()

            if not response_from_db:
                raise EntityNotFoundError("Отклик не найден")

            updated_response = update_fields(response_update_dto.model_dump(), response_from_db)

            session.add(updated_response)
            await session.commit()
            await session.refresh(updated_response)

        return to_model(response_from_db, ResponseModel)

    async def delete(self, id: int, user_id: int):
        async with self.session() as session:
            query = select(Response).filter_by(id=id, user_id=user_id).limit(1)
            res = await session.execute(query)
            response_from_db = res.scalars().first()

            if not response_from_db:
                raise EntityNotFoundError("Отклик не найден")
            else:
                await session.delete(response_from_db)
                await session.commit()

        # return to_model(response_from_db, ResponseModel)

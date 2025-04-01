from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from interfaces import IRepositoryAsync
from models import Job as JobModel
from models import Response as ResponseModel
from repositories.exceptions import EntityNotFoundError
from storage.sqlalchemy.tables import Job
from tools import update_fields
from web.schemas import JobCreateSchema


class JobRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, job_create_dto: JobCreateSchema) -> JobModel:
        async with self.session() as session:
            job = Job(
                user_id=job_create_dto.user_id,
                title=job_create_dto.title,
                description=job_create_dto.description,
                salary_from=job_create_dto.salary_from,
                salary_to=job_create_dto.salary_to,
                is_active=job_create_dto.is_active,
            )

            session.add(job)
            await session.commit()
            await session.refresh(job)

        return self.__to_job_model(job_from_db=job)

    async def retrieve(self, include_relations: bool = False, **kwargs) -> JobModel:
        async with self.session() as session:
            query = select(Job).filter_by(**kwargs).limit(1)
            if include_relations:
                query = query.options(selectinload(Job.responses))

            res = await session.execute(query)
            job_from_db = res.scalars().first()

        job_model = self.__to_job_model(
            job_from_db=job_from_db, include_relations=include_relations
        )
        return job_model

    async def retrieve_many(
        self, limit: int = 100, skip: int = 0, include_relations: bool = False
    ) -> list[JobModel]:
        async with self.session() as session:
            query = select(Job).limit(limit).offset(skip)
            if include_relations:
                query = query.options(selectinload(Job.responses))

            res = await session.execute(query)
            jobs_from_db = res.scalars().all()

        jobs_model = []
        for job in jobs_from_db:
            model = self.__to_job_model(job_from_db=job, include_relations=include_relations)
            jobs_model.append(model)

        return jobs_model

    async def update(self, id: int, job_update_dto: JobCreateSchema) -> JobModel:
        async with self.session() as session:
            query = select(Job).filter_by(id=id).limit(1)
            res = await session.execute(query)
            job_from_db = res.scalars().first()

            if not job_from_db:
                raise EntityNotFoundError("Вакансия не найдена")

            updated_job = update_fields(job_update_dto.model_dump(), job_from_db)

            session.add(updated_job)
            await session.commit()
            await session.refresh(updated_job)

        new_job = self.__to_job_model(job_from_db)
        return new_job

    async def delete(self, id: int):
        async with self.session() as session:
            query = select(Job).filter_by(id=id).limit(1)
            res = await session.execute(query)
            job_from_db = res.scalars.first()

            if not job_from_db:
                raise EntityNotFoundError("Вакансия не найдена")
            else:
                await session.delete(job_from_db)
                await session.commit()

        return self.__to_job_model(job_from_db)

    @staticmethod
    def __to_job_model(job_from_db: Job, include_relations: bool = False) -> JobModel:
        job_responses = []
        job_model = None

        if job_from_db:
            if include_relations:
                job_responses = [
                    ResponseModel(id=response.id) for response in job_from_db.responses
                ]

            job_model = JobModel(
                id=job_from_db.id,
                user_id=job_from_db.user_id,
                title=job_from_db.title,
                description=job_from_db.description,
                salary_from=job_from_db.salary_from,
                salary_to=job_from_db.salary_to,
                is_active=job_from_db.is_active,
                responses=job_responses,
            )

        return job_model

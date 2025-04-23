from interfaces.i_repository import IRepositoryAsync
from repositories.exceptions import EntityNotFoundError
from services.exception import JobNotFoundError
from web.schemas.job import JobCreateSchema, JobUpdateSchema


class JobService:
    def __init__(self, job_repository: IRepositoryAsync, user_repository: IRepositoryAsync):
        self.job_repository = job_repository
        self.user_repository = user_repository

    async def create(self, user_id: int, is_company: bool, job_create_dto: JobCreateSchema):
        if not is_company:
            raise PermissionError("Содавать вакансии могут только компании")

        return await self.job_repository.create(user_id=user_id, job_create_dto=job_create_dto)

    async def retrieve(self, **kwargs):
        try:
            return await self.job_repository.retrieve(**kwargs)
        except EntityNotFoundError as e:
            raise JobNotFoundError("Вакансия не найдена") from e

    async def retrieve_many(self, limit: int, skip: int):
        return await self.job_repository.retrieve_many(limit=limit, skip=skip)

    async def update(self, id: int, job_update_dto: JobUpdateSchema, user_id: int):
        try:
            job = await self.job_repository.retrieve(id=id)
            if job.user_id != user_id:
                raise PermissionError("Недостаточно прав")

            return await self.job_repository.update(id=id, job_update_dto=job_update_dto)
        except EntityNotFoundError as e:
            raise JobNotFoundError("Вакансия не найдена") from e

    async def delete(self, id: int, user_id: int):
        try:
            return await self.job_repository.delete(id=id, user_id=user_id)
        except EntityNotFoundError as e:
            raise JobNotFoundError("Вакансия не найдена") from e

from repositories.exceptions import EntityNotFoundError
from repositories.job_repository import JobRepository
from repositories.user_repository import UserRepository
from services.exception import JobNotFoundError, UserNotFoundError
from web.schemas.job import JobCreateSchema


class JobService:
    def __init__(self, job_repository: JobRepository, user_repository: UserRepository):
        self.job_repository = job_repository
        self.user_repository = user_repository

    async def create(self, job_create_dto: JobCreateSchema):
        try:
            user = await self.user_repository.retrieve(id=job_create_dto.user_id)
        except EntityNotFoundError as e:
            raise UserNotFoundError(e)

        if not user.is_company:
            raise PermissionError("Содавать вакансии могут только компании")

        return await self.job_repository.create(job_create_dto)

    async def retrieve(self, **kwargs):
        try:
            return await self.job_repository.retrieve(**kwargs)
        except EntityNotFoundError as e:
            raise JobNotFoundError(e)

    async def retrieve_many(self, limit: int, skip: int):
        return await self.job_repository.retrieve_many(limit=limit, skip=skip)

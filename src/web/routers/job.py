from dataclasses import asdict
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from dependencies.containers import ServicesContainer
from dependencies.current_user import get_current_user
from models.user import User
from services import JobService
from services.exception import JobNotFoundError, ResponseAlreadyExistsError, ResponseCreationError
from services.response import ResponseService
from web.schemas.common import RetrieveManyParams
from web.schemas.job import JobCreateSchema, JobSchema, JobUpdateSchema
from web.schemas.response import ResponseCreateSchema, ResponseSchema

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_job(
    job_create_dto: JobCreateSchema,
    job_service: JobService = Depends(Provide[ServicesContainer.job_service]),
    current_user: User = Depends(get_current_user),
) -> JobSchema:
    try:
        user = await job_service.create(
            user_id=current_user.id,
            is_company=current_user.is_company,
            job_create_dto=job_create_dto,
        )
        return JobSchema(**asdict(user))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("")
@inject
async def read_jobs(
    params: Annotated[RetrieveManyParams, Query()],
    job_service: JobService = Depends(Provide[ServicesContainer.job_service]),
) -> list[JobSchema]:

    return await job_service.retrieve_many(params.limit, params.skip)


@router.get("/{id}")
@inject
async def read_job(
    id: int, job_service: JobService = Depends(Provide[ServicesContainer.job_service])
) -> JobSchema:
    try:
        return await job_service.retrieve(id=id)
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id}")
@inject
async def update_job(
    id: int,
    job_update_dto: JobUpdateSchema,
    job_service: JobService = Depends(Provide[ServicesContainer.job_service]),
    current_user: User = Depends(get_current_user),
) -> JobSchema:
    try:
        updated_job = await job_service.update(
            id=id, job_update_dto=job_update_dto, user_id=current_user.id
        )
        return JobSchema(**asdict(updated_job))
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_job(
    id: int,
    job_service: JobService = Depends(Provide[ServicesContainer.job_service]),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        await job_service.delete(id=id, user_id=current_user.id)
        return
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/{id}/response", status_code=status.HTTP_201_CREATED)
@inject
async def create_response(
    id: int,
    response_create_dto: ResponseCreateSchema,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
    current_user: User = Depends(get_current_user),
):
    try:
        return await response_service.create(
            user_id=current_user.id,
            job_id=id,
            is_company=current_user.is_company,
            response_create_dto=response_create_dto,
        )
    except (ResponseCreationError, ResponseAlreadyExistsError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.get("/{id}/responses")
@inject
async def get_responses_by_job_id(
    id: int, job_service: JobService = Depends(Provide[ServicesContainer.job_service])
) -> list[ResponseSchema]:
    try:
        job = await job_service.retrieve(id=id, include_relations=True)
        return job.responses
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

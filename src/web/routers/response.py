from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.containers import ServicesContainer
from services import ResponseService
from services.exception import (
    ResponseAlreadyExistsError,
    ResponseCreationError,
    ResponseNotFoundError,
)
from web.schemas import ResponseCreateSchema
from web.schemas.response import ResponseSchema, ResponseUpdateSchema

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_response(
    response_create_dto: ResponseCreateSchema,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
):
    try:
        return await response_service.create(response_create_dto)
    except (ResponseCreationError, ResponseAlreadyExistsError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("")
@inject
async def get_responses(
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
):
    return await response_service.retrieve_many(id=id)


@router.get("/{id}")
@inject
async def read_response(
    id: int,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
) -> ResponseSchema:
    try:
        return await response_service.retrieve(id=id)
    except ResponseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.put("/{id}")
@inject
async def update_response(
    id: int,
    response_update_dto: ResponseUpdateSchema,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
) -> ResponseSchema:
    try:
        updated_response = await response_service.update(
            id=id, response_update_dto=response_update_dto
        )
        return ResponseSchema(**asdict(updated_response))

    except ResponseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_response(
    id: int,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
) -> None:
    try:
        await response_service.delete(id=id)
        return
    except ResponseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

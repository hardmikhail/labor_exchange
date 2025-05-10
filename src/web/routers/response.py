from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.containers import ServicesContainer
from dependencies.current_user import get_current_user
from models.user import User
from services import ResponseService
from services.exception import ResponseNotFoundError
from web.schemas.response import ResponseSchema, ResponseUpdateSchema

router = APIRouter(prefix="/responses", tags=["responses"])


@router.get("")
@inject
async def get_responses(
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
):
    return await response_service.retrieve_many()


@router.get("/{id}")
@inject
async def read_response(
    id: int,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    try:
        return await response_service.retrieve(id=id, user_id=current_user.id)
    except ResponseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.put("/{id}")
@inject
async def update_response(
    id: int,
    response_update_dto: ResponseUpdateSchema,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    try:
        updated_response = await response_service.update(
            id=id,
            user_id=current_user.id,
            response_update_dto=response_update_dto,
        )
        return ResponseSchema(**asdict(updated_response))

    except ResponseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_response(
    id: int,
    response_service: ResponseService = Depends(Provide[ServicesContainer.response_service]),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        await response_service.delete(id=id, user_id=current_user.id)
        return
    except ResponseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

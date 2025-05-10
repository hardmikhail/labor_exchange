from dataclasses import asdict
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from dependencies import get_current_user
from dependencies.containers import ServicesContainer
from models import User
from services import UserService
from services.exception import UserAlreadyExistsError, UserNotFoundError
from web.schemas import RetrieveManyParams, UserCreateSchema, UserSchema, UserUpdateSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
@inject
async def read_users(
    params: Annotated[RetrieveManyParams, Query()],
    user_service: UserService = Depends(Provide[ServicesContainer.user_service]),
) -> list[UserSchema]:

    users_model = await user_service.retrieve_many(params.limit, params.skip)

    users_schema = []
    for model in users_model:
        users_schema.append(
            UserSchema(
                id=model.id,
                name=model.name,
                email=model.email,
                is_company=model.is_company,
            )
        )
    return users_schema


@router.get("/{id}")
@inject
async def read_user(
    id: int,
    user_service: UserService = Depends(Provide[ServicesContainer.user_service]),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    if id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    try:
        return await user_service.retrieve(id=id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    user_create_dto: UserCreateSchema,
    user_service: UserService = Depends(Provide[ServicesContainer.user_service]),
) -> UserSchema:
    try:
        user = await user_service.create(user_create_dto)
        return UserSchema(**asdict(user))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/{id}")
@inject
async def update_user(
    id: int,
    user_update_schema: UserUpdateSchema,
    user_service: UserService = Depends(Provide[ServicesContainer.user_service]),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    if id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    try:
        updated_user = await user_service.update(current_user.id, user_update_schema)
        return UserSchema(**asdict(updated_user))

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    id: int,
    user_service: UserService = Depends(Provide[ServicesContainer.user_service]),
    current_user: User = Depends(get_current_user),
) -> None:
    if id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    try:
        await user_service.delete(id=id)
        return
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

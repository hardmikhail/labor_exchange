from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.containers import ServicesContainer
from repositories import UserRepository
from tools.security import create_access_token, verify_password
from web.schemas import LoginSchema, TokenSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def login(
    login_data: LoginSchema,
    user_service: UserRepository = Depends(Provide[ServicesContainer.user_service]),
) -> TokenSchema:
    user = await user_service.retrieve(email=login_data.email, include_relations=False)

    if user is None or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректное имя пользователя или пароль",
        )

    return TokenSchema(access_token=create_access_token({"sub": user.email}), token_type="Bearer")

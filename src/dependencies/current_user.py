from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status

from dependencies.containers import ServicesContainer
from models import User
from repositories import UserRepository
from tools.security import JWTBearer, decode_access_token


@inject
async def get_current_user(
    user_service: UserRepository = Depends(Provide[ServicesContainer.user_service]),
    token: str = Depends(JWTBearer()),
) -> User:
    cred_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Credentials are not valid"
    )
    payload = decode_access_token(token)
    if payload is None:
        raise cred_exception
    email: str = payload.get("sub")
    if email is None:
        raise cred_exception
    user = await user_service.retrieve(email=email, include_relations=False)
    if user is None:
        raise cred_exception
    return user

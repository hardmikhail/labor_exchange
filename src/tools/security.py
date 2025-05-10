import datetime

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from jose import jwt
from passlib.context import CryptContext

from config.auth import AuthSettings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_settings = AuthSettings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    if not pwd_context.verify(password, hash):
        raise ValueError()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(minutes=auth_settings.access_token_expire_minutes)
        }
    )
    return jwt.encode(to_encode, auth_settings.secret_key, algorithm=auth_settings.algorithm)


def decode_access_token(token: str):
    try:
        encoded_jwt = jwt.decode(
            token, auth_settings.secret_key, algorithms=[auth_settings.algorithm]
        )
    except jwt.JWSError:
        return None
    return encoded_jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials = await super(JWTBearer, self).__call__(request)
        exp = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid auth token")
        if credentials:
            token = decode_access_token(credentials.credentials)
            if token is None:
                raise exp
            return credentials.credentials
        else:
            raise exp

from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, StringConstraints, model_validator
from typing_extensions import Self


class UserSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_company: bool


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_company: Optional[bool] = None


class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=32)]
    password2: str
    is_company: bool = False

    @model_validator(mode="after")
    def password_match(self) -> Self:
        if self.password != self.password2:
            raise ValueError("Пароли не совпадают")
        return self

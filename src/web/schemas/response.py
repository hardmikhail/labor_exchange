from typing import Optional

from pydantic import BaseModel


class ResponseSchema(BaseModel):
    id: int
    job_id: int
    user_id: int
    message: Optional[str] = None


class ResponseCreateSchema(BaseModel):
    message: Optional[str] = None


class ResponseUpdateSchema(ResponseCreateSchema):
    pass

from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class JobSchema(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: bool
    created_at: datetime


class JobUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: Optional[bool] = None


class JobCreateSchema(BaseModel):
    user_id: int
    title: str
    description: str
    salary_from: Decimal = Field(ge=0)
    salary_to: Decimal = Field(ge=0)
    is_active: bool = True
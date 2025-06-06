from decimal import Decimal
from typing import Optional, Self

from pydantic import BaseModel, model_validator


class SalaryValidationMixin:
    @model_validator(mode="after")
    def validate_salary(self) -> Self:
        if self.salary_from and self.salary_to:
            if self.salary_from > self.salary_to:
                raise ValueError("Зарплата 'от' не может быть больше зарплаты 'до'")
        return self


class JobSchema(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    salary_from: Optional[Decimal]
    salary_to: Optional[Decimal]
    is_active: bool


class JobCreateSchema(BaseModel, SalaryValidationMixin):
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: Optional[bool] = None


class JobUpdateSchema(JobCreateSchema):
    pass

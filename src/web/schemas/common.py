from pydantic import BaseModel, Field


class RetrieveManyParams(BaseModel):
    limit: int = Field(default=100, gt=0)
    skip: int = Field(default=0, ge=0)

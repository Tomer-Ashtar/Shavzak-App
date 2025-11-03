from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkerBase(BaseModel):
    name: str = Field(..., min_length=1)
    title: Optional[str] = None
    hard_chores_counter: int = 0
    outer_partner_counter: int = 0


class WorkerCreate(WorkerBase):
    pass


class WorkerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    title: Optional[str] = None
    hard_chores_counter: Optional[int] = None
    outer_partner_counter: Optional[int] = None


class WorkerRead(WorkerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


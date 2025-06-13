from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str


class UpdateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    priority: str

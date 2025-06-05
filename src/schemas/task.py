from typing import Optional

from pydantic import BaseModel


class Task(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

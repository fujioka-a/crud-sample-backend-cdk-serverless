from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str
    title: str = Field(..., max_length=50)
    description: str | None = None
    due_date: str
    status: str
    priority: str

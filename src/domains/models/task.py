from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


PRIORITY_DICT = {
    "LOW": TaskPriority.LOW,
    "MEDIUM": TaskPriority.MEDIUM,
    "HIGH": TaskPriority.HIGH,
    "URGENT": TaskPriority.URGENT,
}


class Task(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority

    @classmethod
    def create(cls, title: str, description: str, due_date: str, priority: str) -> "Task":
        return cls(
            id=uuid4(),
            title=title,
            description=description,
            due_date=due_date,
            status=TaskStatus.TODO,
            priority=PRIORITY_DICT[priority],
        )

    def update(self, updated_task: "Task") -> "Task":
        """
        タスクの属性を更新します。

        :param updated_task: 更新後のタスクデータ
        :return: 更新されたタスク
        """
        return Task(
            id=self.id,
            title=updated_task.title or self.title,
            description=updated_task.description or self.description,
            due_date=updated_task.due_date or self.due_date,
            status=updated_task.status or self.status,
            priority=updated_task.priority or self.priority,
        )

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from ..models.task import Task


class ITaskRepository(ABC):
    @abstractmethod
    def list_tasks(self) -> List[Task]:
        pass

    @abstractmethod
    def create_task(self, task: Task) -> None:
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Task:
        pass

    @abstractmethod
    def update_task(self, updated_task: Task) -> None:
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> None:
        pass

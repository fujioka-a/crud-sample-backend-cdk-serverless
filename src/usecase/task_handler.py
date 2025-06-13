from typing import List
from uuid import UUID

from ..domains.interfaces.task_repository import ITaskRepository
from ..domains.models.task import Task, TaskPriority, TaskStatus
from ..exceptions.errors import DataNotFoundError, InvalidParameterError
from ..routers.dto.task import CreateTaskRequest, UpdateTaskRequest


class TaskManager:
    def __init__(self, repository: ITaskRepository):
        """
        TaskManager の初期化

        :param repository: データ操作を行うリポジトリインターフェース
        """
        self.repository = repository

    def list_tasks(self) -> List[Task]:
        """
        すべてのタスクを取得する

        :return: タスクのリスト
        """
        return self.repository.list_tasks()

    def create_task(self, request: CreateTaskRequest):
        """
        新しいタスクを作成する

        :param task: 作成するタスク
        :return: 作成されたタスク
        """
        if not request.title:
            raise InvalidParameterError("title", request.title or "", "Title is required for creating a task.")

        new_task = Task.create(
            title=request.title,
            description=request.description or "",
            due_date=request.due_date or "",
            priority=request.priority,
        )
        self.repository.create_task(new_task)
        return new_task

    def get_task(self, task_id: str) -> Task:
        """
        指定された ID のタスクを取得する

        :param task_id: タスクの ID
        :return: タスク
        :raises DataNotFoundError: タスクが見つからない場合
        """
        return self.repository.get_task(task_id)

    def update_task(self, task_id: str, request: UpdateTaskRequest) -> Task:
        """
        指定された ID のタスクを更新する

        :param task_id: 更新するタスクの ID
        :param updated_task: 更新後のタスクデータ
        :raises DataNotFoundError: タスクが見つからない場合
        """
        existing_task = self.get_task(task_id)

        updated = Task(
            id=existing_task.id,
            title=request.title,
            description=request.description or existing_task.description,
            due_date=request.due_date or existing_task.due_date,
            status=TaskStatus(request.status) if request.status else existing_task.status,
            priority=TaskPriority(request.priority) if request.priority else existing_task.priority,
        )
        self.repository.update_task(updated)
        return updated

    def delete_task(self, task_id: str) -> None:
        """
        指定された ID のタスクを削除する

        :param task_id: 削除するタスクの ID
        :raises DataNotFoundError: タスクが見つからない場合
        """
        self.repository.delete_task(task_id)

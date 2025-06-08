from typing import List

from ..exception.errors import DataNotFoundError
from ..repositories.interfaces import ITaskRepository
from ..schemas.task import Task


class TaskService:
    def __init__(self, repository: ITaskRepository):
        """
        TaskService の初期化

        :param repository: データ操作を行うリポジトリインターフェース
        """
        self.repository = repository

    def list_tasks(self) -> List[Task]:
        """
        すべてのタスクを取得する

        :return: タスクのリスト
        """
        return self.repository.list_tasks()

    def create_task(self, task: Task) -> Task:
        """
        新しいタスクを作成する

        :param task: 作成するタスク
        :return: 作成されたタスク
        """
        return self.repository.create_task(task)

    def get_task(self, task_id: str) -> Task:
        """
        指定された ID のタスクを取得する

        :param task_id: タスクの ID
        :return: タスク
        :raises DataNotFoundError: タスクが見つからない場合
        """
        return self.repository.get_task(task_id)

    def update_task(self, task_id: str, updated_task: Task) -> Task:
        """
        指定された ID のタスクを更新する

        :param task_id: 更新するタスクの ID
        :param updated_task: 更新後のタスクデータ
        :return: 更新されたタスク
        """
        return self.repository.update_task(task_id, updated_task)

    def delete_task(self, task_id: str) -> None:
        """
        指定された ID のタスクを削除する

        :param task_id: 削除するタスクの ID
        :raises DataNotFoundError: タスクが見つからない場合
        """
        self.repository.delete_task(task_id)

    def upsert_task(self, task_id: str, task: Task) -> Task:
        """
        指定された ID のタスクを更新または作成する (Upsert)

        :param task_id: タスクの ID
        :param task: 更新または作成するタスクデータ
        :return: 更新または作成されたタスク
        """
        try:
            # 既存のタスクが存在する場合は更新
            return self.repository.update_task(task_id, task)
        except DataNotFoundError:
            # タスクが存在しない場合は新規作成
            return self.repository.create_task(task)

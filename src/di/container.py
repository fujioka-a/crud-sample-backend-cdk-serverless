from injector import Injector, Module, provider, singleton

from ..domains.interfaces.task_repository import ITaskRepository
from ..infrastructure.repositories.task_repository import TaskDynamoDBRepository
from ..usecase.task_handler import TaskManager


class AppModule(Module):
    @singleton
    @provider
    def provide_task_repository(self) -> ITaskRepository:
        # DynamoDBリポジトリを使用する
        return TaskDynamoDBRepository(table_name="tasks")

    @singleton
    @provider
    def provide_task_service(self, repo: ITaskRepository) -> TaskManager:
        return TaskManager(repo)


injector = Injector([AppModule()])

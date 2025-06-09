from injector import Injector, Module, provider, singleton

from ..domains.interfaces.task_repository import ITaskRepository
from ..repositories.task_repository import TaskDynamoDBRepository
from ..services.task_service import TaskService


class AppModule(Module):
    @singleton
    @provider
    def provide_task_repository(self) -> ITaskRepository:
        # DynamoDBリポジトリを使用する
        return TaskDynamoDBRepository(table_name="tasks")

    @singleton
    @provider
    def provide_task_service(self, repo: ITaskRepository) -> TaskService:
        return TaskService(repo)


injector = Injector([AppModule()])

from injector import Injector, Module, provider, singleton

from src.dependencies.auth import AuthService
from src.repositories.task_repository import TaskDynamoDBRepository
from src.services.task_service import TaskService


class AppModule(Module):
    @singleton
    @provider
    def provide_auth_service(self) -> AuthService:
        return AuthService()

    @singleton
    @provider
    def provide_task_repository(self) -> TaskDynamoDBRepository:
        return TaskDynamoDBRepository(table_name="tasks")

    @singleton
    @provider
    def provide_task_service(self, repo: TaskDynamoDBRepository) -> TaskService:
        return TaskService(repo)


injector = Injector([AppModule()])

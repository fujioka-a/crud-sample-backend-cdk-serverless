from ..models.task import Task


class TaskService:
    def __init__(self, task_repository):
        self.task_repository = task_repository

    def handle_task(self, task: Task):
        # ドメインロジックをここに実装
        pass

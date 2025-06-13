import pytest

from src.domains.interfaces.task_repository import ITaskRepository
from src.domains.models.task import Task, TaskPriority, TaskStatus
from src.exceptions.errors import DataNotFoundError
from src.routers.dto.task import CreateTaskRequest, UpdateTaskRequest
from src.usecase.task_handler import TaskManager


class FakeRepository(ITaskRepository):
    def __init__(self):
        self.tasks = {}

    def list_tasks(self):
        return list(self.tasks.values())

    def create_task(self, task):
        self.tasks[task.id] = task

    def get_task(self, task_id):
        if task_id not in self.tasks:
            raise DataNotFoundError(resource_name="Task")
        return self.tasks[task_id]

    def update_task(self, updated_task):
        if updated_task.id not in self.tasks:
            raise DataNotFoundError(resource_name="Task")
        self.tasks[updated_task.id] = updated_task

    def delete_task(self, task_id):
        if task_id not in self.tasks:
            raise DataNotFoundError()
        del self.tasks[task_id]


@pytest.fixture
def service():
    return TaskManager(FakeRepository())


import uuid


def make_task(
    id=None, title="t", description="d", due_date="2025-01-01", status=TaskStatus.TODO, priority=TaskPriority.HIGH
):
    if id is None:
        id = str(uuid.uuid4())
    return Task(id=id, title=title, description=description, due_date=due_date, status=status, priority=priority)


def make_task_request(title="t", description="d", due_date="2025-01-01", priority="HIGH"):
    return CreateTaskRequest(title=title, description=description, due_date=due_date, priority=priority)


def test_create_task(service):
    task_request = CreateTaskRequest(title="t", description="d", due_date="2025-01-01", priority="HIGH")

    # Act
    service.create_task(task_request)

    # Assert
    result = service.list_tasks()[0]
    assert result.title == task_request.title
    assert result.description == task_request.description
    assert result.due_date == task_request.due_date
    assert result.priority == TaskPriority[task_request.priority.upper()]


def test_list_tasks(service):
    # FakeRepositoryにタスクを追加
    service.create_task(make_task_request(title="Task 1"))
    service.create_task(make_task_request(title="Task 2"))

    tasks = service.list_tasks()

    # Assert
    assert len(tasks) == 2

    titles = [task.title for task in tasks]
    assert "Task 1" in titles and "Task 2" in titles


def test_update_task(service):
    service.create_task(make_task_request(title="original"))

    result_id = service.list_tasks()[0].id

    # Act
    response = service.update_task(
        result_id,
        UpdateTaskRequest(
            title="updated", description="new desc", due_date="2025-01-02", status="TODO", priority="MEDIUM"
        ),
    )

    # Assert
    assert response.id == result_id
    assert response.title == "updated"
    assert response.description == "new desc"
    assert response.due_date == "2025-01-02"
    assert response.status == TaskStatus.TODO
    assert response.priority == TaskPriority.MEDIUM


def test_delete_task(service):
    service.create_task(make_task_request(title="Task to delete"))

    pre_res = service.list_tasks()
    assert len(pre_res) == 1
    assert pre_res[0].title == "Task to delete"

    service.delete_task(pre_res[0].id)
    post_res = service.list_tasks()
    assert len(post_res) == 0

    with pytest.raises(DataNotFoundError):
        service.get_task(pre_res[0].id)

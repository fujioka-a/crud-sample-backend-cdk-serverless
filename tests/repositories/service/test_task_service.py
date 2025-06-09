import pytest

from src.domains.interfaces.task_repository import ITaskRepository
from src.domains.models.task import Task
from src.exceptions.errors import DataNotFoundError
from src.services.task_service import TaskService


class FakeRepository(ITaskRepository):
    def __init__(self):
        self.tasks = {}

    def list_tasks(self):
        return list(self.tasks.values())

    def create_task(self, task):
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id):
        if task_id not in self.tasks:
            raise DataNotFoundError(resource_name="Task")
        return self.tasks[task_id]

    def update_task(self, task_id, updated_task):
        if task_id not in self.tasks:
            raise DataNotFoundError(resource_name="Task")
        self.tasks[task_id] = updated_task
        return updated_task

    def delete_task(self, task_id):
        if task_id not in self.tasks:
            raise DataNotFoundError()
        del self.tasks[task_id]


@pytest.fixture
def service():
    return TaskService(FakeRepository())


def make_task(id="1", title="t", description="d", due_date="2025-01-01", status="open", priority="high"):
    return Task(id=id, title=title, description=description, due_date=due_date, status=status, priority=priority)


def test_create_and_get_task(service):
    task = make_task()
    service.create_task(task)
    result = service.get_task("1")
    assert result.id == "1"
    assert result.title == "t"


def test_list_tasks(service):
    task1 = make_task(id="1")
    task2 = make_task(id="2", title="t2")
    service.create_task(task1)
    service.create_task(task2)
    tasks = service.list_tasks()
    assert len(tasks) == 2
    ids = {t.id for t in tasks}
    assert "1" in ids and "2" in ids


def test_update_task(service):
    task = make_task()
    service.create_task(task)
    updated = make_task(title="updated")
    result = service.update_task("1", updated)
    assert result.title == "updated"
    assert service.get_task("1").title == "updated"


def test_delete_task(service):
    task = make_task()
    service.create_task(task)
    service.delete_task("1")
    with pytest.raises(DataNotFoundError):
        service.get_task("1")


def test_upsert_task_update(service):
    task = make_task()
    service.create_task(task)
    updated = make_task(title="upserted")
    result = service.upsert_task("1", updated)
    assert result.title == "upserted"
    assert service.get_task("1").title == "upserted"


def test_upsert_task_create(service):
    new_task = make_task(id="2", title="new")
    result = service.upsert_task("2", new_task)
    assert result.id == "2"
    assert service.get_task("2").title == "new"

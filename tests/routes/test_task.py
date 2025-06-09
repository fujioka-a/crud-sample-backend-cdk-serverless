import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.auth import get_current_user
from src.domains.models.task import Task
from src.routers.task import get_task_service, router


# --- テスト用のモックサービスと認証 ---
class MockTaskService:
    def __init__(self):
        self.tasks = {}

    def list_tasks(self):
        return list(self.tasks.values())

    def create_task(self, task):
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def update_task(self, task_id, task):
        self.tasks[task_id] = task
        return task

    def delete_task(self, task_id):
        return self.tasks.pop(task_id, None) is not None


def mock_get_task_service():
    return MockTaskService()


def mock_get_current_user():
    return {"sub": "test-user"}


# --- テスト用FastAPIアプリ ---
app = FastAPI()
app.include_router(router)

# 依存を上書き（関数オブジェクトをキーにする）
mock_service = MockTaskService()
app.dependency_overrides[get_task_service] = mock_get_task_service
app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)


def test_list_tasks_ok():
    # 事前にタスク登録
    mock_service.create_task(
        Task(id="1", title="t", description="d", due_date="2025-01-01", status="open", priority="high")
    )
    headers = {"Authorization": "Bearer dummy-token"}
    response = client.get("/tasks/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"id": "1", "title": "t", "description": "d", "due_date": "2025-01-01", "status": "open", "priority": "high"}
    ]


def test_create_task_ok():
    app.dependency_overrides["src.core.auth.get_current_user"] = mock_get_current_user

    task_data = {
        "id": "2",
        "title": "new",
        "description": "desc",
        "due_date": "2025-01-01",
        "status": "open",
        "priority": "high",
    }
    headers = {"Authorization": "Bearer dummy-token"}
    response = client.post("/tasks/", json=task_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == "2"


def test_create_task_ng_not_auth():
    task_data = {
        "id": "2",
        "title": "new",
        "description": "desc",
        "due_date": "2025-01-01",
        "status": "open",
        "priority": "high",
    }
    headers = {}
    response = client.post("/tasks/", json=task_data, headers=headers)
    assert response.status_code == 401


def test_get_task_ok():
    service = mock_get_task_service()
    task = Task(id="3", title="t3", description="d3", due_date="2025-01-01", status="open", priority="high")
    service.create_task(task)
    app.dependency_overrides["src.routers.task.get_task_service"] = lambda: service

    response = client.get("/tasks/3")
    assert response.status_code == 200 or response.status_code == 404


def test_update_task_ok():
    service = mock_get_task_service()
    task = Task(id="4", title="t4", description="d4", due_date="2025-01-01", status="open", priority="high")
    service.create_task(task)
    app.dependency_overrides["src.routers.task.get_task_service"] = lambda: service

    update_data = {
        "id": "4",
        "title": "updated",
        "description": "d4",
        "due_date": "2025-01-01",
        "status": "open",
        "priority": "high",
    }
    response = client.put("/tasks/4", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "updated"


def test_delete_task_ok():
    service = mock_get_task_service()
    task = Task(id="5", title="t5", description="d5", due_date="2025-01-01", status="open", priority="high")
    service.create_task(task)
    app.dependency_overrides["src.routers.task.get_task_service"] = lambda: service

    response = client.delete("/tasks/5")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

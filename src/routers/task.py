from dto.task import CreateTaskRequest, UpdateTaskRequest
from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import get_current_user
from ..di.container import injector
from ..domains.models.task import Task
from ..usecase.task_handler import TaskManager

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_service() -> TaskManager:
    return injector.get(TaskManager)


# routing section ==========================================================


@router.get("/", response_model=list[Task])
def list_tasks(service: TaskManager = Depends(get_task_service), user: dict = Depends(get_current_user)):
    return service.list_tasks()


@router.post("/", response_model=Task, status_code=201)
def create_task(
    request: CreateTaskRequest,
    service: TaskManager = Depends(get_task_service),
    user: dict = Depends(get_current_user),
):
    return service.create_task(request)


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: str,
    service: TaskManager = Depends(get_task_service),
    user: dict = Depends(get_current_user),
):
    return service.get_task(task_id)


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    service: TaskManager = Depends(get_task_service),
    user: dict = Depends(get_current_user),
):
    return service.update_task(task_id, request)


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    service: TaskManager = Depends(get_task_service),
    user: dict = Depends(get_current_user),
):
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import get_current_user
from ..di.container import injector
from ..domains.models.task import Task
from ..services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_service() -> TaskService:
    return injector.get(TaskService)


# routing section ==========================================================


@router.get("/", response_model=list[Task])
def list_tasks(service: TaskService = Depends(get_task_service), user: dict = Depends(get_current_user)):
    return service.list_tasks()


@router.post("/", response_model=Task)
def create_task(task: Task, service: TaskService = Depends(get_task_service), user: dict = Depends(get_current_user)):
    return service.create_task(task)


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
    user: dict = Depends(get_current_user),
):
    return service.get_task(task_id)


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    task: Task,
    service: TaskService = Depends(get_task_service),
    user: dict = Depends(get_current_user),
):
    return service.update_task(task_id, task)


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
    user: dict = Depends(get_current_user),
):
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

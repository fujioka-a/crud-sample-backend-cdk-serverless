from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_current_user
from ..repositories.task_repository import TaskDynamoDBRepository
from ..schemas.task import Task

TASK_TABLE_NAME = "tasks"  # DynamoDB テーブル名を指定

router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(get_current_user)])

# DynamoDB テーブル名を指定
task_repository = TaskDynamoDBRepository(table_name=TASK_TABLE_NAME)


@router.get("/", response_model=list[Task])
def list_tasks():
    return task_repository.list_tasks()


@router.post("/", response_model=Task)
def create_task(task: Task):
    return task_repository.create_task(task)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    task = task_repository.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: str, task: Task):
    updated_task = task_repository.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete("/{task_id}")
def delete_task(task_id: str):
    success = task_repository.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

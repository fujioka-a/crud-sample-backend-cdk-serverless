from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..repositories.task_repository import TaskDynamoDBRepository
from ..schemas.task import Task

TASK_TABLE_NAME = "tasks"  # DynamoDB テーブル名を指定

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# DynamoDB テーブル名を指定
task_repository = TaskDynamoDBRepository(table_name=TASK_TABLE_NAME)


@router.get("/", response_model=list[Task])
def list_tasks(user=Depends(get_current_user)):
    return task_repository.list_tasks()


@router.post("/", response_model=Task)
def create_task(task: Task, user=Depends(get_current_user)):
    return task_repository.create_task(task)

from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..schemas.task import Task

router = APIRouter(prefix="/tasks", tags=["Tasks"])

fake_db = []  # デモ用


@router.get("/", response_model=list[Task])
def list_tasks(user=Depends(get_current_user)):
    return fake_db


@router.post("/", response_model=Task)
def create_task(task: Task, user=Depends(get_current_user)):
    fake_db.append(task)
    return task

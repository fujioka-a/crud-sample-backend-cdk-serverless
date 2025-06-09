from fastapi import APIRouter, Depends

from ..core.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def read_current_user(user=None):
    user = user or Depends(get_current_user)
    return {"username": user["username"]}

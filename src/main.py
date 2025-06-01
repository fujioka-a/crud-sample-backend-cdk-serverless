from fastapi import FastAPI

from .routers import task, user

app = FastAPI(title="Serverless FastAPI with Cognito")

app.include_router(user.router)
app.include_router(task.router)

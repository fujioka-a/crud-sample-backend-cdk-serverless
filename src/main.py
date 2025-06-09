from fastapi import FastAPI

from .routers import task

app = FastAPI(title="Serverless FastAPI with Cognito")

# app.include_router(user.router)
app.include_router(task.router)

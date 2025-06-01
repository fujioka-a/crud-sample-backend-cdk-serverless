# src/handler.py
from aws_lambda_powertools.utilities.typing import LambdaContext
from mangum import Mangum

from .main import app  # FastAPI アプリ

handler = Mangum(app)

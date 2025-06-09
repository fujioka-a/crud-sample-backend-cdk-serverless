import os
from functools import lru_cache


class Settings:
    region: str = os.getenv("AWS_REGION", "ap-northeast-1")
    user_pool_id: str = os.getenv("USER_POOL_ID", "")
    app_client_id: str = os.getenv("APP_CLIENT_ID", "")


@lru_cache
def get_settings():
    return Settings()

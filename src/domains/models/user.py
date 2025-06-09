from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, validator


class Sex(Enum):
    MEN = "men"
    WOMEN = "women"
    UNKNOWN = "unknown"


class User(BaseModel):
    id: str
    email: str = Field(..., max_length=100)
    name: str = Field(..., max_length=50)
    birth_date: date
    sex: Sex

    @validator("birth_date")
    def validate_birth_date(self, v):
        if v > date.today():
            raise ValueError("誕生日は未来の日付にできません")
        return v

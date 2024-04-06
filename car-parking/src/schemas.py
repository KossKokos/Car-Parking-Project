from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

from fastapi import Path
from pydantic_settings import SettingsConfigDict

from src.database.models import Role


class UserResponse(BaseModel):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    sex: str
    role: Role
    avatar: str | None
    forbidden: bool


class UserModel(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    email: EmailStr
    sex: str
    password: str = Field(min_length=6, max_length=16)


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

from fastapi import Path, HTTPException
from pydantic_settings import SettingsConfigDict

from src.database.models import Role, User 
from src.database import db 

from sqlalchemy.orm import Session


class UserResponse(BaseModel):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    avatar: str | None
    forbidden: bool
    plate_number: str


class UserModel(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6, max_length=16)
    plate_number: str


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


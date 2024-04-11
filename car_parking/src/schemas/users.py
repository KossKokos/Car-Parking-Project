from datetime import datetime
from typing import Optional
from ..schemas.parking import CurrentParking
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=15, default='username')
    email: EmailStr = Field(default='example@gmail.com')
    password: str = Field(min_length=8, max_length=15, default='password')
    license_plate: str
    # tariff_id: int = 2

      
class UserResponse(BaseModel):
    username: str = 'username'
    email: EmailStr = 'example@gmail.com'
    license_plate: str


class UserParkingResponse(BaseModel):
    user: UserResponse
    parking: CurrentParking | str

    class Config:
        orm_mode = True



class ChangePassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=15, default='new_password')


class UserRoleUpdate(BaseModel):
    role: str = "role"


class UserByCarResponse(BaseModel):
    id: int
    username: str = 'username'
    email: EmailStr = 'example@gmail.com'
    created_at: datetime
    confirmed: bool
    license_plate: str
    banned: bool
    tariff: int
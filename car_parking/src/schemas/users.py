from typing import Optional
from ..schemas.parking import CurrentParking
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=15, default='username')
    email: EmailStr = Field(default='example@gmail.com')
    password: str = Field(min_length=8, max_length=15, default='password')
    license_plate: str

class UserResponce(BaseModel):
    username: str = 'username'
    email: EmailStr = 'example@gmail.com'
    license_plate: str


class UserParkingResponse(BaseModel):
    user: UserResponce
    parking: CurrentParking | str


    class Config:
        orm_mode = True





class ChangePassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=15, default='new_password')


class UserRoleUpdate(BaseModel):
    role: str = "role"


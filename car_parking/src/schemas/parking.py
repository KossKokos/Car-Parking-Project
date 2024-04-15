from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class ParkingResponse(BaseModel):
    id: int
    enter_time: datetime
    departure_time: datetime | None
    license_plate: str
    amount_paid: float | None
    duration: float | None
    status: bool


class ParkingInfo(BaseModel):
    user: str
    total_payment_amount: float
    total_parking_time: float
    parking_info: List[ParkingResponse] | None


class CurrentParking(BaseModel):
    enter_time: datetime
    time_on_parking: float
    parking_cost: float


class ParkingSchema(BaseModel):
    info: ParkingResponse
    status: str
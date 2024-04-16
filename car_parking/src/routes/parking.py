import io
from PIL import Image

from fastapi import APIRouter, Depends, status, BackgroundTasks, Request, UploadFile, File, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import numpy as np

from ..database.db import get_db
from ..database.models import User, Tariff
from ..repository import users as repository_users
from ..repository import parking as repository_parking
from ..repository import tariff as repository_tariff
from ..repository.logout import token_to_blacklist
from ..services.auth import service_auth
from ..services.plate_reader import pr as PlateReader
from ..schemas.users import UserResponse, UserParkingResponse
from ..schemas.parking import ParkingInfo, ParkingSchema, ParkingResponse
from ..conf.extensions import EXTENSIONS
from ..services import (
    email as service_email,
    roles as service_roles,
)


router = APIRouter(prefix="/parking", tags=["parking"])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.post('/parking/{license_plate}',
             response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def enter_parking(background_tasks: BackgroundTasks,
                        request: Request, 
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db)):
    
    valid_ext = await repository_parking.is_valid_file_ext(file)
    if not valid_ext:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file extension")
    
    request_object_content = await file.read()
    img = Image.open(io.BytesIO(request_object_content))
    img = np.array(img, dtype="uint8")
    license_plate = await PlateReader.get_prediction(img)

    if license_plate is None:
        return "License plate not found, please send better picture where car is visible"
    
    parking_place = await repository_parking.entry_to_the_parking(license_plate, db)
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    if user:
        enter_time = parking_place.info.enter_time.strftime("%Y-%m-%d %H:%M:%S")
        tariff = await repository_tariff.get_tariff_by_tariff_id(user.tariff_id, db)
        background_tasks.add_task(
            service_email.praking_enter_message,
            user.email,
            user.username,
            user.license_plate,
            enter_time,
            tariff.tariff_name,
            tariff.tariff_value,
            request.base_url,
        )
    return parking_place


#exit code second version
@router.post('/exit_parking/{license_plate}',
             response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def exit_parking( background_tasks: BackgroundTasks,
                        request: Request,
                        file: UploadFile = File(...), 
                        db: Session = Depends(get_db)):
    valid_ext = await repository_parking.is_valid_file_ext(file)
    if not valid_ext:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file extension")
    
    request_object_content = await file.read()
    img = Image.open(io.BytesIO(request_object_content))
    img = np.array(img, dtype="uint8")
    license_plate = await PlateReader.get_prediction(img)

    if license_plate is None:
        return "License plate not found, please send better picture where car is visible"
   
    parking_place = await repository_parking.get_parking_place_by_car_license_plate(license_plate, db)
    if parking_place:
        parking_info = await repository_parking.exit_from_the_parking(license_plate, db)
        user = await repository_users.get_user_by_car_license_plate(license_plate, db)
        if user:
            enter_time = parking_info.info.enter_time.strftime("%Y-%m-%d %H:%M:%S")
            departure_time = parking_info.info.departure_time.strftime("%Y-%m-%d %H:%M:%S")
            tariff = await repository_tariff.get_tariff_by_tariff_id(user.tariff_id, db)
            background_tasks.add_task(
                service_email.praking_exit_message,
                user.email,
                user.username,
                user.license_plate,
                parking_place.id,
                enter_time,
                departure_time,
                tariff.tariff_name,
                tariff.tariff_value,
                parking_info.info.duration,
                parking_info.info.amount_paid,
                request.base_url,
            )
        return parking_info
    else:
        return f"Parking place for car {license_plate} not found"

@router.get('/confirm_payment/{parking_place_id}',
            response_model=ParkingSchema | str, 
            status_code=status.HTTP_202_ACCEPTED)
async def confirm_payment(parking_place_id: str, db: Session = Depends(get_db)):
    parking_staus = await repository_parking.change_parking_status_authorised(parking_place_id, db)
    return parking_staus


@router.get(
    "/free_place/{date}",
    status_code=status.HTTP_200_OK,
)
async def occupied_places(date: str, db: Session = Depends(get_db)):
    occupied = await repository_parking.free_parking_places(date, db)
    return occupied

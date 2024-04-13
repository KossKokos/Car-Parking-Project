from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer,OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User, Tariff
# from ..repository import users as repository_users
# from ..repository import parking as repository_parking
# from ..repository import tariff as repository_tariff
from ..repository.logout import token_to_blacklist
from ..services.auth import service_auth
from ..schemas.users import UserResponse, UserParkingResponse
# from car_parking.src.repository import admin as repository_admin
from ..schemas.parking import ParkingInfo, ParkingSchema, ParkingResponse
from ..repository import (
    users as repository_users,
    parking as repository_parking,
    tariff as repository_tariff,
    admin as repository_admin
)
from ..services import (
    email as service_email,
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
)
from ..schemas import (
    users as schema_users,
    token as schema_token,
    email as schema_email,
)


router = APIRouter(prefix='/parking', tags=['parking'])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.post('/parking/{license_plate}',
             response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def enter_parking(license_plate,
                        background_tasks: BackgroundTasks,
                        request: Request, 
                        db: Session = Depends(get_db)):
    license_plate = license_plate.upper()
    parking_place = await repository_parking.entry_to_the_parking(license_plate, db)
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    if user: 
        enter_time = parking_place.info.enter_time.strftime("%Y-%m-%d %H:%M:%S")
        tariff = await repository_tariff.get_tariff_by_tariff_id(user.tariff_id, db)
        background_tasks.add_task(service_email.praking_enter_message, 
                                user.email, 
                                user.username,
                                user.license_plate,
                                enter_time,
                                tariff.tariff_name,
                                tariff.tariff_value,
                                request.base_url)
    return parking_place


#exit code second version
@router.post('/exit_parking/{license_plate}',
             response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def exit_parking(license_plate,     
                        background_tasks: BackgroundTasks,
                        request: Request, 
                        db: Session = Depends(get_db)):
    license_plate = license_plate.upper()
    parking_place = await repository_parking.get_parking_place_by_car_license_plate(license_plate, db)
    print(parking_place.id)
    parking_info = await repository_parking.exit_from_the_parking(license_plate, db)
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    if user:
        enter_time = parking_info.info.enter_time.strftime("%Y-%m-%d %H:%M:%S")
        departure_time = parking_info.info.departure_time.strftime("%Y-%m-%d %H:%M:%S")
        tariff = await repository_tariff.get_tariff_by_tariff_id(user.tariff_id, db)                                  
        background_tasks.add_task(service_email.praking_exit_message,
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
                            request.base_url)
    return parking_info


@router.get('/confirm_payment/{parking_place_id}', 
            status_code=status.HTTP_202_ACCEPTED)
async def confirm_payment(parking_place_id: str, db: Session = Depends(get_db)):
    await repository_parking.change_parking_status_authorised(parking_place_id, db)
    return {'detail': 'Payment confirmed'}


@router.get('/free_place/{date}',
            #  dependencies=[Depends(service_logout.logout_dependency),
            #                Depends(allowd_operation),
            #                Depends(service_banned.banned_dependency)],
            #  response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def occupied_places(date: str, db: Session = Depends(get_db)):
    occupied = await repository_parking.free_parking_places(date, db)
    return occupied




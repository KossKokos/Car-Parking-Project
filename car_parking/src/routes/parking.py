from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer,OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User, Tariff
from ..repository import users as repository_users
from ..repository import parking as repository_parking
from ..repository import tariff as repository_tariff
from ..repository.logout import token_to_blacklist
from ..services.auth import service_auth
from ..schemas.users import UserResponse, UserParkingResponse
from ..schemas.parking import ParkingInfo, ParkingSchema, ParkingResponse
from ..services import (
    email as service_email,
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
)
from ..services import (
    email as service_email,
    roles as service_roles,
    banned as service_banned,
    logout as service_logout
)

router = APIRouter(prefix='/parking', tags=['parking'])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.post('/parking/{license_plate}',
             #dependencies=[Depends(service_logout.logout_dependency), 
                           #Depends(allowd_operation),
                           #Depends(service_banned.banned_dependency)],

             response_model=ParkingSchema,
             status_code=status.HTTP_200_OK,
             )

async def enter_parking(license_plate, 
                        #current_user: User = Depends(service_auth.get_current_user),
                        db: Session = Depends(get_db),
                        background_tasks: BackgroundTasks = BackgroundTasks()):
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
                                Request.base_url)
    return parking_place



#exit code second version
@router.post('/exit_parking/{license_plate}',
             response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def exit_parking(license_plate, 
                       db: Session = Depends(get_db),
                       background_tasks: BackgroundTasks = BackgroundTasks()):
    license_plate = license_plate.upper()
    parking_place = await repository_parking.get_parking_place_by_car_license_plate(license_plate, db)
    print(parking_place.id)
    parking_info = await repository_parking.exit_from_the_parking(license_plate, db)
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    if user:
        enter_time = parking_info.info.enter_time.strftime("%Y-%m-%d %H:%M:%S")
        #departure_time = parking_info.info.departure_time.strftime("%Y-%m-%d %H:%M:%S")
        departure_time = parking_info.info.departure_time
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
                            Request.base_url)
    return parking_info


@router.get('/confirm_payment/{token}', status_code=status.HTTP_202_ACCEPTED)
# async def confirm_payment(parking_place_id: int, db: Session = Depends(get_db)):
#     parking_place = await repository_parking.change_parking_status(parking_place_id, db)
#     return parking_place
async def print_msg():
    print("Confirmed!")

#example 1
# @router.patch('/change_password/{token}', status_code=status.HTTP_202_ACCEPTED)
# async def reset_password(body: schema_users.ChangePassword, token: str, db: Session = Depends(get_db)):
#     """
#     The reset_password function is used to reset a user's password.
#         It takes in the body of the request, which contains a new_password field, and a token that was sent to the user's email address.
#         The function decodes the token using service_auth.decode_email_token(token), and then uses repository_users.get_user_by_email() to get 
#         information about that user from our database (db). If no such user exists, we return an HTTPException with status code 400 (Bad Request) 
#         and detail 'Verification error'. Otherwise we hash their new password using
    
#     :param body: ChangePassword: Get the new password from the request body
#     :param token: str: Get the token from the url
#     :param db: Session: Get the database session
#     :return: A string
#     """
#     email = await service_auth.decode_email_token(token)
#     user = await repository_users.get_user_by_email(email, db)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
#     body.new_password = service_auth.get_password_hash(body.new_password)
#     await repository_users.change_password(user, body.new_password, db)
#     return {"detail": "User's password was changed succesfully"}


# exampl 2
# @router.get('/confirmed_email/{token}', status_code=status.HTTP_202_ACCEPTED)
# async def confirm_email(token: str, db: Session = Depends(get_db)):
#     """
#     The confirm_email function is used to confirm a user's email address.
#         The function takes in the token that was sent to the user's email and decodes it,
#         then checks if there is a user with that email address in the database. If there isn't,
#         an error message will be returned. If there is, we check if their account has already been confirmed or not. 
#         If it has been confirmed already, we return a message saying so; otherwise we update their account as being confirmed.
    
#     :param token: str: Get the token from the url
#     :param db: Session: Get a database session
#     :return: A dict with a message key
#     """
#     email = await service_auth.decode_email_token(token)
#     user = await repository_users.get_user_by_email(email, db)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
#     if user.confirmed:
#         return {'detail': 'Email is already confirmed'}
#     await repository_users.confirmed_email(email, db)
#     return {'detail': 'Email is confirmed'}

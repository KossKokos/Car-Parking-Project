from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer,OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User
from ..repository import users as repository_users
from ..repository import parking as repository_parking
from ..repository.logout import token_to_blacklist
from ..services.auth import service_auth
from ..schemas.users import UserResponse, UserParkingResponse
from ..schemas.parking import ParkingInfo, ParkingSchema
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

#original code
# @router.post('/parking/{license_plate}',
#              response_model=ParkingSchema,
#              status_code=status.HTTP_200_OK,
#              )
# async def enter_parking(license_plate, db: Session = Depends(get_db)):
#     parking_place = await repository_parking.entry_to_the_parking(license_plate, db)
#     return parking_place

@router.post('/parking/{license_plate}',
             dependencies=[Depends(service_logout.logout_dependency), 
                           Depends(allowd_operation),
                           Depends(service_banned.banned_dependency)],
             response_model=ParkingSchema,
             status_code=status.HTTP_200_OK,
             )
async def enter_parking(license_plate, 
                        current_user: User = Depends(service_auth.get_current_user),
                        db: Session = Depends(get_db)):
    parking_place = await repository_parking.entry_to_the_parking(license_plate, db)
    return parking_place


# @router.post('/parking/{license_plate}',
#             # dependencies=[
#             #             Depends(service_logout), 
#             #             Depends(allowd_operation),
#             #             #Depends(service_banned)
#             #             ],
#              response_model=ParkingSchema,
#              status_code=status.HTTP_200_OK,
#              )
# async def enter_parking(license_plate,
#                         credentials: HTTPAuthorizationCredentials = Security(security),
#                         current_user: User = Depends(service_auth.get_current_user),
#                         db: Session = Depends(get_db),
#                         background_tasks: BackgroundTasks = BackgroundTasks()):
#     #parking_place = await repository_parking.entry_to_the_parking(license_plate, db)
#     #return parking_place
#     background_tasks.add_task(service_email.praking_enter_message, current_user.email, current_user.username, Request.base_url)
#     #return {'Parking place': parking_place, 'detail': 'Parking place successfully created, please check your email for details'}
#     return {'detail': 'Parking place successfully created, please check your email for details'}

# original code
# @router.post('/exit_parking/{license_plate}',
#              response_model=ParkingSchema | str,
#              status_code=status.HTTP_200_OK,
#              )
# async def exit_parking(license_plate, db: Session = Depends(get_db)):
#     parking_info = await repository_parking.exit_from_the_parking(license_plate, db)
#     return parking_info

@router.post('/exit_parking/{license_plate}',
             dependencies=[Depends(service_logout.logout_dependency), 
                           Depends(allowd_operation),
                           Depends(service_banned.banned_dependency)],
             response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def exit_parking(license_plate, 
                       current_user: User = Depends(service_auth.get_current_user),
                       db: Session = Depends(get_db)):
    parking_info = await repository_parking.exit_from_the_parking(license_plate, db)
    return parking_info

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User
from ..repository import users as repository_users
from ..repository import parking as repository_parking
from ..services.auth import service_auth
from ..schemas.users import UserResponce, UserParkingResponse
from ..schemas.parking import ParkingInfo, ParkingSchema
from ..services import (
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
    cloudinary as service_cloudinary
)

router = APIRouter(prefix='/parking', tags=['parking'])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "moderator", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.post('/parking/{license_plate}',
             response_model=ParkingSchema,
             status_code=status.HTTP_200_OK,
             )
async def enter_parking(license_plate, db: Session = Depends(get_db)):
    parking_place = await repository_parking.entry_to_the_parking(license_plate, db)
    return parking_place


@router.post('/exit_parking/{license_plate}',
             response_model=ParkingSchema | str,
             status_code=status.HTTP_200_OK,
             )
async def exit_parking(license_plate, db: Session = Depends(get_db)):
    parking_info = await repository_parking.exit_from_the_parking(license_plate, db)
    return parking_info

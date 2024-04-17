from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from car_parking.src.database.db import get_db
from car_parking.src.database.models import User
from car_parking.src.repository import users as repository_users
from car_parking.src.services.auth import service_auth
from car_parking.src.schemas.users import UserParkingResponse
from car_parking.src.schemas.parking import ParkingInfo
from car_parking.src.services import (
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
)

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.get(
    "/me",
    response_model=UserParkingResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation),
        Depends(service_banned.banned_dependency),
    ],
)
async def read_users_me(
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    user = await repository_users.get_user_me(current_user, db)
    return user


@router.get(
    "/profile",
    response_model=ParkingInfo,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation),
        Depends(service_banned.banned_dependency),
    ],
    description="Any User",
)
async def get_user_profile(
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    user_profile = await repository_users.get_parking_info(
        current_user.license_plate, db
    )

    return user_profile

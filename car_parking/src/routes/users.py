from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User
from ..repository import users as repository_users
from ..services.auth import service_auth
from ..schemas.users import UserResponce, UserParkingResponse
from ..schemas.parking import ParkingInfo
from ..services import (
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
)

router = APIRouter(prefix='/users', tags=['users'])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "moderator", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.get('/me', response_model=UserParkingResponse,z
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency),
                          Depends(allowd_operation),
                          Depends(service_banned.banned_dependency)]
            )
async def read_users_me(current_user: User = Depends(service_auth.get_current_user), db: Session = Depends(get_db)):

    user = await repository_users.get_user_me(current_user, db)
    return user


@router.get('/profile', response_model=ParkingInfo,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency),
                          Depends(allowd_operation),
                          Depends(service_banned.banned_dependency)],
            description="Any User")
async def get_user_profile(current_user: User = Depends(service_auth.get_current_user), db: Session = Depends(get_db)):
    """
    The get_user_profile function returns a user profile by username.
        Args:
            username (str): The name of the user to get.
    
    :param username: Get the username
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database connection
    :return: A dictionary
    """
    user_profile = await repository_users.get_parking_info(current_user, db)

    return user_profile

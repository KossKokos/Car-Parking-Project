from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User
from ..repository import users as repository_users
from ..services.auth import service_auth
from ..schemas.users import UserResponse
from ..services import (
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
    cloudinary as service_cloudinary
)


router = APIRouter(prefix='/users', tags=['users'])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "moderator", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])

# transferd to routes/admin.py 
# @router.get('/',
#             status_code=status.HTTP_200_OK,
#             dependencies=[Depends(service_logout.logout_dependency), 
#                           Depends(allowd_operation),
#                           Depends(service_banned.banned_dependency)]
 
#           )
# async def get_all_usernames(current_user: User = Depends(service_auth.get_current_user),
#                             db: Session = Depends(get_db)):
#     """
#     The get_all_usernames function returns a list of all usernames in the database.
    
#     :param current_user: User: Get the current user from the database
#     :param db: Session: Get the database session from the dependency injection
#     :return: A list of all the usernames in the database
#     """
#     usernames = await repository_users.return_all_users(db)
#     return usernames


@router.get('/me', response_model=UserResponse,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation),
                          Depends(service_banned.banned_dependency)]
            )
async def read_users_me(current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_users_me function returns the current user's information.

        get:
          summary: Returns the current user's information.
          description: Returns the current user's information based on their JWT token in their request header.
          responses: HTTP status code 200 indicates success! In this case, it means we successfully returned a User
    
    :param current_user: User: Get the user object of the current user
    :return: The user object
    """
    return current_user


@router.get('/{username}', 
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation),
                          Depends(service_banned.banned_dependency)],
            description = "Any User")
async def get_user_profile(username, 
                           current_user: User = Depends(service_auth.get_current_user),
                           db: Session = Depends(get_db)):
    """
    The get_user_profile function returns a user profile by username.
        Args:
            username (str): The name of the user to get.
    
    :param username: Get the username
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database connection
    :return: A dictionary
    """
    
    user = await repository_users.get_user_by_username(username, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'User with username: {username} not found.')
    
    # quantity_of_loaded_images: int = await repository_users.get_imagis_quantity(user, db)

    user_profile = {
                    "user id": user.id,
                    "username":user.username,
                    "email": user.email,
                    "registrated at":user.created_at,
                    "banned": user.banned,
                    "user role":user.role,
                    "license_plates": license_plate, # type: ignore
                    }

    return user_profile


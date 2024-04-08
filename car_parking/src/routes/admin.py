from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User
from ..repository import users as repository_users, admin as repository_admin
from ..services.auth import service_auth
from ..schemas.users import UserResponce, UserRoleUpdate
from ..services import (
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
    cloudinary as service_cloudinary
)


router = APIRouter(prefix='/admin', tags=['admin'])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.get('/',
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation_by_admin)]
            )
async def get_all_usernames(current_user: User = Depends(service_auth.get_current_user),
                            db: Session = Depends(get_db)):
    """
    The get_all_usernames function returns a list of all usernames in the database.
    
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session from the dependency injection
    :return: A list of all the usernames in the database
    """
    usernames = await repository_admin.return_all_users(db)
    return usernames



@router.patch('/ban/{user_id}', 
                        response_model=UserResponce, 
                        status_code=status.HTTP_200_OK,
                        dependencies=[Depends(service_logout.logout_dependency), 
                                      Depends(allowd_operation_by_admin)],
                        )
async def ban_user(user_id:str,
                                credentials: HTTPAuthorizationCredentials = Security(security), 
                                current_user: User = Depends(service_auth.get_current_user),
                                db: Session = Depends(get_db)):
    """
    The update_banned_status function updates the banned status of a user.
        Only admin can ban the user.
        User cannot change own banned status.
        Superadmin status cannot be changed.
    
    :param user_id:str: Get the user_id from the url
    :param body: BannedUserUpdate: Get the banned status from the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Access the database
    :return: The user object
    """

    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user.id:
        raise HTTPException(status_code=403, detail="Permission denied. User cannot change own banned status.")
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied.Superadmin status cannot be changed.")

    await repository_users.update_banned_status(user, db)
    return user

@router.patch('/unban/{user_id}', 
                        response_model=UserResponce, 
                        status_code=status.HTTP_200_OK,
                        dependencies=[Depends(service_logout.logout_dependency), 
                                      Depends(allowd_operation_by_admin)],
                        )
async def unban_user(user_id:str,
                                credentials: HTTPAuthorizationCredentials = Security(security), 
                                current_user: User = Depends(service_auth.get_current_user),
                                db: Session = Depends(get_db)):
    """
    The update_banned_status function updates the banned status of a user.
        Only admin can ban the user.
        User cannot change own banned status.
        Superadmin status cannot be changed.
    
    :param user_id:str: Get the user_id from the url
    :param body: BannedUserUpdate: Get the banned status from the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Access the database
    :return: The user object
    """

    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user.id:
        raise HTTPException(status_code=403, detail="Permission denied. User cannot change own banned status.")
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied.Superadmin status cannot be changed.")

    await repository_users.update_unbanned_status(user, db)
    return user

@router.delete('/{user_id}',
               status_code=status.HTTP_200_OK,
               dependencies=[Depends(service_logout.logout_dependency), 
                             Depends(allowd_operation_by_admin)])
async def delete_user(user_id: int, current_user: User = Depends(service_auth.get_current_user),
                      db: Session = Depends(get_db)):
    """
        The delete_user function allows an admin to delete a user.

    :param user_id: int: ID of the user to be deleted
    :param current_user: User: Get the current user from the database
    :param db: Session: Database session
    :return: dict
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
      
    if current_user.id != 1 and user.role == "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Only supreadmin can delede other admin.")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Permission denied. Cannot delete own account.")
    
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied. Superadmin user cannot be deleted.")

    await repository_users.delete_user(user_id, db)
    return {"message": f"User successfully deleted"}


@router.patch('/change_role/{user_id}', response_model=UserResponce, 
                                        status_code=status.HTTP_202_ACCEPTED,
                                        dependencies=[Depends(service_logout.logout_dependency), 
                                                      Depends(allowd_operation_by_admin)])
async def change_user_role(
    user_id: int,
    body: UserRoleUpdate,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The change_user_role function allows an admin to change the role of a user.
    
    :param user_id: int: Fetch the user by id from the database
    :param body: UserRoleUpdate: Get the new role from the request body
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the function
    :return: A user object with udated role
    :doc-author: Trelent
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Only admin can change roles.")
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Permission denied. Own role cannot be changed.")
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied.Superadmin role cannot be changed.")
    if user.role == "admin" and current_user.id != 1:
        raise HTTPException(status_code=403, detail="Permission denied.Admin role can be changed only by Superadmin (id=1).")

    if body.role in ['admin', 'user']:
        await repository_admin.change_user_role(user, body, db)
        return user
    else:
        raise HTTPException(status_code=400, detail="Invalid role provided")
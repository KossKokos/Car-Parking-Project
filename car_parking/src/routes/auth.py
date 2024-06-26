from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from car_parking.src.database.db import get_db
from car_parking.src.database.models import User
from car_parking.src.repository import users as repository_users
from car_parking.src.repository import car as repository_car
from car_parking.src.repository.logout import token_to_blacklist
from car_parking.src.services.auth import service_auth
from car_parking.src.services import (
    email as service_email,
    roles as service_roles,
    banned as service_banned,
    logout as service_logout,
)
from car_parking.src.schemas import (
    users as schema_users,
    token as schema_token,
    email as schema_email,
)


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

allowd_operation_by_admin = service_roles.RoleRights(["admin"])
allowd_operation_any_user = service_roles.RoleRights(["user", "admin"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    body: schema_users.UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    exist_user_with_email: User = await repository_users.get_user_by_email(
        body.email, db
    )

    if exist_user_with_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {body.email} already exists",
        )

    exist_user_with_username: User = await repository_users.get_user_by_username(
        body.username, db
    )

    if exist_user_with_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with name: {body.username} already exists",
        )

    exist_user_with_license = await repository_users.get_user_by_car_license_plate(
        body.license_plate, db
    )

    if exist_user_with_license:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with license plate: {body.license_plate} already exists",
        )

    body.password = service_auth.get_password_hash(body.password)
    car = await repository_car.get_car_by_license_plate(body.license_plate.upper(), db)
    if not car:
        car = await repository_car.create_car(body.license_plate.upper(), db)
    user = await repository_users.create_user(body, db)
    print(request.base_url)
    background_tasks.add_task(
        service_email.send_email, user.email, user.username, request.base_url
    )
    return {
        "user": user,
        "detail": f"User successfully created, please check your email << {user.email} >> for verification",
    }


@router.post(
    "/login",
    response_model=schema_token.TokenResponce,
    status_code=status.HTTP_202_ACCEPTED,
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if user.banned == True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {user.email} banned. Please contact your administrator!",
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email is not confirmed"
        )
    if not service_auth.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    access_token = await service_auth.create_access_token(data={"sub": user.email})
    refresh_token = await service_auth.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/refresh_token",
    response_model=schema_token.TokenResponce,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_any_user),
        Depends(service_banned.banned_dependency),
    ],
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    token = current_user.refresh_token
    email = await service_auth.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User with this token doesn't exist",
        )

    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await service_auth.create_access_token(data={"sub": email})
    refresh_token = await service_auth.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}", status_code=status.HTTP_202_ACCEPTED)
async def confirm_email(token: str, db: Session = Depends(get_db)):
    email = await service_auth.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"detail": "Email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"detail": "Email is confirmed"}


@router.post("/request_email", status_code=status.HTTP_202_ACCEPTED)
async def request_email(
    body: schema_email.RequestEmail,
    background_task: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is not None and user.confirmed:
        return {"detail": "Email is already confirmed"}
    if user:
        background_task.add_task(
            service_email.send_email, user.email, user.username, request.base_url
        )
    return {"detail": "Check your email for further information"}


@router.post("/reset_password", status_code=status.HTTP_202_ACCEPTED)
async def reset_password_request(
    body: schema_email.RequestEmail,
    background_task: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        background_task.add_task(
            service_email.send_reset_password_email,
            user.email,
            user.username,
            request.base_url,
        )
    return {"detail": "Check your email for further information"}


@router.patch("/change_password/{token}", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(
    body: schema_users.ChangePassword, token: str, db: Session = Depends(get_db)
):
    email = await service_auth.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    body.new_password = service_auth.get_password_hash(body.new_password)
    await repository_users.change_password(user, body.new_password, db)
    return {"detail": "User's password was changed succesfully"}


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_any_user),
    ],
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
    current_user: User = Depends(service_auth.get_current_user),
):
    access_token = credentials.credentials
    user_id = current_user.id
    result = await token_to_blacklist(access_token, user_id, db)
    return {"message": f"User {current_user.email} successfully logged out"}

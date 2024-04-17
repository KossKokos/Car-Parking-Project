from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Security,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from car_parking.src.database.db import get_db
from car_parking.src.database.models import User
from car_parking.src.repository import (
    users as repository_users,
    admin as repository_admin,
    car as repository_cars,
)
from car_parking.src.schemas.parking import ParkingInfo
from car_parking.src.services.auth import service_auth
from car_parking.src.schemas.users import UserResponse, UserRoleUpdate, UserByCarResponse

from car_parking.src.services import (
    roles as service_roles,
    logout as service_logout,
)


router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def get_all_usernames(
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    usernames = await repository_admin.return_all_users(db)
    return usernames


@router.patch(
    "/ban/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def ban_user(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user.id:
        raise HTTPException(
            status_code=403,
            detail="Permission denied. User cannot change own banned status.",
        )
    if user.id == 1:
        raise HTTPException(
            status_code=403,
            detail="Permission denied.Superadmin status cannot be changed.",
        )

    await repository_admin.update_banned_status(user, db)
    return user


@router.patch(
    "/unban/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def unban_user(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user.id:
        raise HTTPException(
            status_code=403,
            detail="Permission denied. User cannot change own banned status.",
        )
    if user.id == 1:
        raise HTTPException(
            status_code=403,
            detail="Permission denied.Superadmin status cannot be changed.",
        )

    await repository_admin.update_unbanned_status(user, db)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != 1 and user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Permission denied. Only supreadmin can delede other admin.",
        )

    if current_user.id == user_id:
        raise HTTPException(
            status_code=403, detail="Permission denied. Cannot delete own account."
        )

    if user.id == 1:
        raise HTTPException(
            status_code=403,
            detail="Permission denied. Superadmin user cannot be deleted.",
        )

    await repository_users.delete_user(user_id, db)
    return {"message": f"User successfully deleted"}


@router.patch(
    "/change_role/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def change_user_role(
    user_id: int,
    body: UserRoleUpdate,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Permission denied. Only admin can change roles."
        )
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user_id:
        raise HTTPException(
            status_code=403, detail="Permission denied. Own role cannot be changed."
        )
    if user.id == 1:
        raise HTTPException(
            status_code=403,
            detail="Permission denied.Superadmin role cannot be changed.",
        )
    if user.role == "admin" and current_user.id != 1:
        raise HTTPException(
            status_code=403,
            detail="Permission denied.Admin role can be changed only by Superadmin (id=1).",
        )

    if body.role in ["admin", "user"]:
        await repository_admin.change_user_role(user, body, db)
        return user
    else:
        raise HTTPException(status_code=400, detail="Invalid role provided")


@router.patch(
    "/ban_car/{license_plate}",
    # response_model=CarResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def ban_car(
    license_plate: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    license_plate = license_plate.upper()
    car = await repository_cars.get_car_by_license_plate(license_plate, db)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    if user and user.id != 1:
        await repository_admin.update_banned_status(user, db)
    await repository_cars.update_car_banned_status(car, db)
    if user:
        car_banned_response = {
            "car id": car.id,
            "license plate": car.license_plate,
            "car ban status": car.banned,
            "banned user id": user.id,
            "banned user email": user.email,
            "user ban status": user.banned,
        }
    else:
        car_banned_response = {
            "car id": car.id,
            "license plate": car.license_plate,
            "car ban status": car.banned,
            "banned user id": "not registered user",
            "banned user email": "N/A",
            "user ban status": "N/A",
        }

    return car_banned_response


@router.patch(
    "/unban_car/{license_plate}",
    # response_model=CarResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def unban_car(
    license_plate: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    license_plate = license_plate.upper()
    car = await repository_cars.get_car_by_license_plate(license_plate, db)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    if user and user.id != 1:
        await repository_admin.update_unbanned_status(user, db)
    await repository_cars.update_car_unbanned_status(car, db)
    if user:
        car_banned_response = {
            "car id": car.id,
            "license plate": car.license_plate,
            "car ban status": car.banned,
            "unbanned user id": user.id,
            "unbanned user email": user.email,
            "user ban status": user.banned,
        }
    else:
        car_banned_response = {
            "car id": car.id,
            "license plate": car.license_plate,
            "car ban status": car.banned,
            "unbanned user id": "not registered user",
            "unbanned user email": "N/A",
            "user ban status": "N/A",
        }

    return car_banned_response


@router.get(
    "/search_user/{license_plate}",
    # response_model=UserByCarResponse | str,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def search_user_by_license_plate(
    license_plate: str, db: Session = Depends(get_db)
):
    license_plate = license_plate.upper()
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    if user:
        return user
    return f"The user with license plate {license_plate} is not registered."


@router.get(
    "/create_csv/{license_plate}/{filename}",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def create_csv_file(
    license_plate: str,
    filename: str,
    db: Session = Depends(get_db),
):
    create_file = await repository_admin.create_parking_csv(license_plate, filename, db)
    return create_file


@router.get(
    "/get_profile/{license_plate}",
    response_model=ParkingInfo | str,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def get_profile_by_car(license_plate: str, db: Session = Depends(get_db)):
    profile = await repository_users.get_parking_info(license_plate, db)
    print(profile)
    return profile


@router.get(
    "/users",
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def get_all_users(db: Session = Depends(get_db)):
    users = await repository_admin.get_all_users(db)
    return users


@router.patch(
    "/change_tariff/{user_id}",
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def change_user_tariff(
    user_id: int,
    new_tariff: str,
    db: Session = Depends(get_db),
):
    try:
        await repository_admin.change_tariff(user_id, new_tariff, db)
        return {"message": "Tariff changed successfully"}
    except HTTPException as e:
        return e


@router.post(
    "/create_tariff/{tariff_name}/{tariff_value}",
    dependencies=[
        Depends(service_logout.logout_dependency),
        Depends(allowd_operation_by_admin),
    ],
)
async def create_tariff(
    tariff_name: str,
    tariff_value: int,
    db: Session = Depends(get_db),
):
    new_tariff = await repository_admin.add_tariff(tariff_name, tariff_value, db)
    return new_tariff

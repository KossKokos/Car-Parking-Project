from car_parking.src.database.models import Tariff, User

from car_parking.src.schemas.users import UserRoleUpdate
import csv
import os
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from typing import Optional, Type
from car_parking.src.repository import users as repository_users
from car_parking.src.services.csv_generator import _build_csv_file_path


async def get_tariff_by_name(
    tariff_name: str,
    db: Session,
) -> Tariff | None:
    return (
        db.query(Tariff)
        .filter(Tariff.tariff_name == tariff_name.upper())
        .first()
    )


async def change_user_role(user: User, body: UserRoleUpdate, db: Session) -> User:
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user


async def delete_user(user_id: int, db: Session) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return None


async def return_all_users(db: Session) -> dict:
    users = db.query(User).all()
    usernames = {f"username(id: {user.id})": user.username for user in users}
    return usernames


async def set_user_banned_status(
    user: User,
    is_banned: bool,
    db: Session,
) -> User:
    user.banned = is_banned
    db.commit()
    db.refresh(user)
    return user


async def create_parking_csv(
    license_plate: str,
    filename: str,
    db: Session,
) -> str:
    normalized_license_plate = license_plate.upper()
    file_path = _build_csv_file_path(filename)

    parking_history = await repository_users.get_parking_info(
        normalized_license_plate,
        db,
    )

    with file_path.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Name",
            "Total Payment Amount",
            "Total Parking Time",
            "enter_time",
            "departure_time",
            "license_plate",
            "amount_paid",
            "duration",
            "status",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for parking_info in parking_history.parking_info:
            writer.writerow(
                {
                    "enter_time": parking_info.enter_time,
                    "departure_time": parking_info.departure_time,
                    "license_plate": parking_info.license_plate,
                    "amount_paid": parking_info.amount_paid,
                    "duration": parking_info.duration,
                    "status": parking_info.status,
                }
            )

        writer.writerow({"Name": parking_history.user})
        writer.writerow({"Total Payment Amount": parking_history.total_payment_amount})
        writer.writerow({"Total Parking Time": parking_history.total_parking_time})

    return f"CSV file created: {file_path.name}"


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.query(User).filter_by(email=email).first()


# async def admin_edit_user(user_id, new_data):
#     user_info = await get_user_by_email(user_id, db)
#     if user_info:
#         user = db.query(User).filter_by(id=user_id).first()
#         for key, value in new_data.items():
#             setattr(user, key, value)
#         try:
#             db.commit()
#             print("Інформація про користувача успішно оновлена.")
#         except Exception as e:
#             db.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
#     else:
#         print("Користувача з таким ID не знайдено.")


async def get_all_users(db: Session) -> list[Type[User]]:
    users = db.query(User).all()
    return users


async def change_tariff(
    user_id: int,
    new_tariff: str,
    db: Session,
) -> User:
    user = await repository_users.get_user_by_id(user_id=user_id, db=db)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    tariff = await get_tariff_by_name(new_tariff, db)

    if tariff is None:
        raise HTTPException(
            status_code=404,
            detail="Tariff not found",
        )

    user.tariff_id = tariff.id

    db.commit()
    db.refresh(user)

    return user


async def add_tariff(
    tariff_name: str,
    tariff_cost: int,
    db: Session,
) -> Tariff:
    normalized_tariff_name = tariff_name.upper()

    existing_tariff = await get_tariff_by_name(
        normalized_tariff_name,
        db,
    )

    if existing_tariff is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Tariff {normalized_tariff_name} already exists",
        )

    new_tariff = Tariff(
        tariff_name=normalized_tariff_name,
        tariff_value=tariff_cost,
    )

    db.add(new_tariff)
    db.commit()
    db.refresh(new_tariff)

    return new_tariff

import csv
import os
from pathlib import Path
from typing import Optional, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from car_parking.src.database.models import Tariff, User
from car_parking.src.repository import users as repository_users
from car_parking.src.schemas.users import UserRoleUpdate


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


async def update_banned_status(user: User, db: Session):
    user.banned = True
    db.commit()
    db.refresh(user)
    return user


async def update_unbanned_status(user: User, db: Session):
    user.banned = False
    db.commit()
    db.refresh(user)
    return user


async def create_parking_csv(license_plate, filename, db: Session):
    default_dir = r"\csv_files"
    path = str(Path(__file__).parent.parent.parent) + default_dir
    file_path = os.path.join(path, f"{filename}.csv")
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    parking_history = await repository_users.get_parking_info(license_plate, db)
    with open(file_path, "w", newline="") as csvfile:
        fieldnames = [
            "Name",
            "Total Payment Amount",
            "Total Parking Time",
            "Parking place ID",
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
                    "Parking place ID": parking_info.id,
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
    return f"CSV file {filename} created succefully"


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
):
    user = await repository_users.get_user_by_id(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tariff = db.query(Tariff).filter(Tariff.tariff_name == new_tariff).first()
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")

    user.tariff_id = tariff.id
    db.commit()
    db.refresh(user)
    return {"message": "Tariff changed successfully"}


async def add_tariff(tariff_name: str, tariff_cost: int, db: Session):
    new_tariff = Tariff(tariff_name=tariff_name, tariff_value=tariff_cost)
    db.add(new_tariff)
    db.commit()
    return f"Tariff {tariff_name} has been created"

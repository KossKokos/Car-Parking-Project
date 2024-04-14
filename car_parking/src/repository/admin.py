from sqlalchemy.orm import Session


from ..database.models import Tariff, User, Car
from ..repository import users as repository_users
from ..schemas.users import UserRoleUpdate
import csv
import os
from pathlib import Path

from typing import Type
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from typing import List, Optional
from ..database import db
from ..repository import users as repository_users
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def change_user_role(user: User, body: UserRoleUpdate, db: Session) -> User:
    """
    The change_user_role function changes the role of a user.
        Args:
            user (User): The User object to change the role of.
            body (UserRoleUpdate): A UserRoleUpdate object containing the new role for this user.
            db (Session): The database session to use when changing this users' role in our database.
    
    :param user: User: Get the user object from the database
    :param body: UserRoleUpdate: Get the role from the request body
    :param db: Session: Access the database
    :return: A user object with updated role
    :doc-author: Trelent
    """
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user
    
    
async def delete_user(user_id: int, db: Session) -> None:
    """
    The delete_user function deletes a user from the database based on the user ID.

    :param user_id: int: ID of the user to be deleted
    :param db: Session: Database session
    :return: None
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return None 


async def return_all_users(db: Session) -> dict:
    """
    The return_all_users function retrieves all usernames from the User table.

    :param db: Session: Database session
    :return: A dictionary containing all usernames from the User table
    """
    users = db.query(User).all()
    usernames = {f"username(id: {user.id})": user.username for user in users}
    return usernames


async def update_banned_status(user: User, db: Session):
    """
    The update_banned_status function updates the banned status of a user for bunned.
        
    
    :param user: User: Get the user that is being updated
    :param body: BannedUserUpdate: Update the user's banned status
    :param db: Session: Access the database
    :return: A user object
    """
    user.banned = True
    db.commit()
    db.refresh(user)
    return user


async def update_unbanned_status(user: User, db: Session):
    """
    The update_гтbanned_status function updates the banned status of a user for unbanned.
        
    
    :param user: User: Get the user that is being updated
    :param body: BannedUserUpdate: Update the user's banned status
    :param db: Session: Access the database
    :return: A user object
    """
    user.banned = False
    db.commit()
    db.refresh(user)
    return user


# async def add_tariff(tariff_name: str, tariff_cost: int, db: Session)


async def create_parking_csv(license_plate, filename, db: Session):
    default_dir = r"\csv_files"
    path = str(Path(__file__).parent.parent.parent) + default_dir
    file_path = os.path.join(path, f"{filename}.csv")
    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    parking_history = await repository_users.get_parking_info(license_plate, db)
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ["Name", 'Total Payment Amount', 'Total Parking Time', 'enter_time', 'departure_time', 'license_plate', 'amount_paid', 'duration', 'status', ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for parking_info in parking_history.parking_info:
            writer.writerow({
                'enter_time': parking_info.enter_time,
                'departure_time': parking_info.departure_time,
                'license_plate': parking_info.license_plate,
                'amount_paid': parking_info.amount_paid,
                'duration': parking_info.duration,
                'status': parking_info.status
            })
        writer.writerow({'Name': parking_history.user})
        writer.writerow({'Total Payment Amount': parking_history.total_payment_amount})
        writer.writerow({'Total Parking Time': parking_history.total_parking_time})
    return "CSV file created"

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
        
        
async def get_all_users(db: Session) -> List[User]:
    users = db.query(User).all()
    return users


async def get_cars_with_user_by_car_number(db: Session, car_number: str):
    car = db.query(Car).filter(Car.license_plate == car_number).first()
    if car:
        user = db.query(User).filter(User.license_plate == car_number).first()
        return car, user
    else:
        return None, None

#current_user: User = None
async def change_tariff(user_id: int, new_tariff: str, db: Session,):
    # async with db.begin():
    user = await repository_users.get_user_by_id(user_id=user_id, db=db)
    # user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # if current_user and current_user.role != "admin":
    #     raise HTTPException(status_code=403, detail="Permission denied. Only admin can change tariffs.")
    tariff = db.query(Tariff).filter(Tariff.tariff_name == new_tariff).first()
    if not tariff:
        raise HTTPException(status_code=404, detail="Tariff not found")
    # if new_tariff not in ["basic", "premium", "holiday_rate"]:
    #     raise HTTPException(status_code=400, detail="Invalid tariff provided")

    user.tariff_id = tariff.id
    db.commit()
    db.refresh(user)
    return {"message": "Tariff changed successfully"}

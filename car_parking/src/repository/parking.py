from datetime import datetime
import pytz

from sqlalchemy.orm import Session
from fastapi import File

from car_parking.src.utils. import parking_helpers as helpers
from ..database.models import Parking, Car, ParkingCount

from ..repository import users as repository_users
from ..repository.car import create_car

from ..conf.constants import PARKING_COUNT_DATA
from ..conf.extensions import EXTENSIONS


async def create_parking_place(license_plate: str, db: Session):
    parking_place = Parking(license_plate=license_plate)

    db.add(parking_place)
    db.commit()
    return parking_place


async def change_parking_status_not_authorised(parking_place_id: int, db: Session):
    parking_place = helpers._get_parking_place_by_id(parking_place_id, db)

    if parking_place is None:
        return "Parking place not found"

    user = helpers._get_user_by_license_plate(parking_place.license_plate, db)

    parking_place = helpers._apply_invoice_to_parking_place(
        parking_place=parking_place,
        user=user,
        db=db,
    )

    parking_place.status = True
    parking_count = helpers._get_parking_count(db)
    
    parking = helpers._build_parking_schema(
        parking_place,
        message="The barrier is open, See you next time!",
    )

    helpers._decrease_occupied_count(parking_count)
    db.commit()
    return parking


async def change_parking_status_authorised(parking_place_id: int, db: Session):
    parking_place = helpers._get_parking_place_by_id(parking_place_id, db)

    if parking_place is None:
        return "Parking place not found"
    parking_place.status = True

    parking_count = helpers._get_parking_count(db)
    
    parking_status = helpers._build_parking_schema(
        parking_place,
        message="The barrier is open, See you next time!",
    )
    
    helpers._decrease_occupied_count(parking_count)
    db.commit()
    return parking_status


async def calculate_invoice(parking_place_id: int, db: Session):
    parking_place = helpers._get_parking_place_by_id(parking_place_id, db)

    if parking_place is None:
        return None
    user = helpers._get_user_by_license_plate(parking_place.license_plate, db)

    parking_place = helpers._apply_invoice_to_parking_place(
        parking_place=parking_place,
        user=user,
        db=db,
    )

    db.commit()
    return parking_place


async def entry_to_the_parking(license_plate: str, db: Session):
    car = db.query(Car).filter(Car.license_plate == license_plate).first()

    parking_count = helpers._get_parking_count(db)
    if helpers._is_parking_full(parking_count):
        return "Sorry we don't have places for parking"

    if not car:
        await create_car(license_plate, db)
    parking_place = helpers._get_active_parking_place_by_license_plate(license_plate, db)

    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    # if user:
    if not parking_place:
        parking_place = await create_parking_place(license_plate, db)
        message = (
            f"Parking successful, please check your email<< {user.email} >> for details"
            if user
            else "Parking successful, to get details please sign up for our Car Parking service"
        )
        parking = helpers._build_parking_schema(parking_place, message=message)
        
        helpers._increase_occupied_count(parking_count)
        db.commit()
        return parking

    parking = helpers._build_parking_schema(
        parking_place,
        message="This car already in parking.",
    )
    return parking


async def exit_from_the_parking(license_plate: str, db: Session):

    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    
    # if user:
    parking_place = helpers._get_active_parking_place_by_license_plate(license_plate, db)
    
    if parking_place:
        parking_place = await calculate_invoice(parking_place.id, db)

        message = (
            f"Parking invoice sent to your email << {user.email}>>. Please confirm payment"
            if user
            else f"Your parking ID = << {parking_place.id} >>Confirm payment, please."
        )

        parking = helpers._build_parking_schema(
            parking_place,
            message=message,
            format_departure_time=True,
        )

        return parking
    return "This car not in parking"


async def seed_parking_count(db: Session):
    if db.query(ParkingCount).count() == 0:
        
        for data in PARKING_COUNT_DATA:
            parking_count = ParkingCount(**data)
            db.add(parking_count)

        db.commit()
    

async def free_parking_places(date: str, db: Session):
    date_format = "%Y.%m.%d %H:%M"
    try:
        dt = datetime.strptime(date, date_format)
        kiev_timezone = pytz.timezone("Europe/Kiev")
        dt = kiev_timezone.localize(dt)
        all_parking = db.query(Parking).all()
        quantity = db.query(ParkingCount).first()
        all_places = 0
        for parking in all_parking:
            if parking.enter_time <= dt and (
                parking.departure_time is None or dt < parking.departure_time
            ):
                all_places += 1
        return all_places
    except Exception:
        return "Wrong date format"


async def is_valid_file_ext(file: File) -> bool:
    file_ext = file.filename.split(".")[-1]
    if file_ext not in EXTENSIONS:
        return False
    return True

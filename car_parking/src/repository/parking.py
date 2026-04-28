from datetime import datetime
import pytz

from sqlalchemy.orm import Session
from fastapi import File

from ..database.models import User, Parking, Car, ParkingCount, Tariff

from ..schemas.parking import ParkingResponse, ParkingSchema

from ..repository import users as repository_users
from ..repository.car import create_car

from ..conf.constants import PARKING_COUNT_DATA, RESPONSE_DATETIME_FORMAT
from ..conf.extensions import EXTENSIONS

from ..services.parking_calculations import (
    calculate_parking_cost,
    calculate_parking_duration_hours,
)


def _format_datetime_for_response(value: datetime | None) -> str | None:
    if value is None:
        return None

    return value.strftime(RESPONSE_DATETIME_FORMAT)


def _build_parking_schema(
    parking_place: Parking,
    message: str,
    *,
    response_status: bool = False,
    format_departure_time: bool = False,
) -> ParkingSchema:
    departure_time = parking_place.departure_time

    if format_departure_time:
        departure_time = _format_datetime_for_response(departure_time)

    return ParkingSchema(
        info=ParkingResponse(
            id=parking_place.id,
            enter_time=_format_datetime_for_response(parking_place.enter_time),
            departure_time=departure_time,
            license_plate=parking_place.license_plate,
            amount_paid=parking_place.amount_paid,
            duration=parking_place.duration,
            status=rfesponse_status,
        ),
        status=message,
    )

async def create_parking_place(license_plate: str, db: Session):
    parking_place = Parking(license_plate=license_plate)

    db.add(parking_place)
    db.commit()
    return parking_place


async def change_parking_status_not_authorised(parking_place_id: int, db: Session):
    parking_place = db.query(Parking).filter(Parking.id == parking_place_id).first()
    user = db.query(User).filter(User.license_plate == parking_place.license_plate).first()
    departure_time = datetime.now(pytz.timezone('Europe/Kiev'))
    duration = calculate_parking_duration_hours(parking_place.enter_time, departure_time)
    parking_place.status = True
    parking_place.departure_time = departure_time
    parking_place.duration = duration
    count = db.query(ParkingCount).first()
    if user:
        tariff = db.query(Tariff).filter_by(id=user.tariff_id).first()
        parking_place.amount_paid = calculate_parking_cost(duration, tariff.tariff_value)
    else:
        tariff = db.query(Tariff).filter_by(id=1).first()
        parking_place.amount_paid = calculate_parking_cost(duration, tariff.tariff_value)

    parking = _build_parking_schema(
        parking_place,
        message="The barrier is open, See you next time!",
    )

    count.occupied_quantity -= 1
    db.commit()
    return parking


async def change_parking_status_authorised(parking_place_id: int, db: Session):
    parking_place = db.query(Parking).filter(Parking.id == parking_place_id).first()
    parking_place.status = True
    count = db.query(ParkingCount).first()
    
    parking_status = _build_parking_schema(
        parking_place,
        message="The barrier is open, See you next time!",
    )
    
    count.occupied_quantity -= 1
    db.commit()
    return parking_status


async def calculate_invoice(parking_place_id: int, db: Session):
    parking_place = db.query(Parking).filter(Parking.id == parking_place_id).first()
    user = (
        db.query(User).filter(User.license_plate == parking_place.license_plate).first()
    )
    departure_time = datetime.now(pytz.timezone("Europe/Kiev"))
    duration = calculate_parking_duration_hours(parking_place.enter_time, departure_time)
    parking_place.departure_time = departure_time
    parking_place.duration = duration
    if user:
        tariff = db.query(Tariff).filter_by(id=user.tariff_id).first()
        parking_place.amount_paid = calculate_parking_cost(duration, tariff.tariff_value)
    else:
        tariff = db.query(Tariff).filter_by(id=1).first()
        parking_place.amount_paid = calculate_parking_cost(duration, tariff.tariff_value)
    db.commit()
    return parking_place


async def entry_to_the_parking(license_plate: str, db: Session):
    car = db.query(Car).filter(Car.license_plate == license_plate).first()

    count = db.query(ParkingCount).first()
    if count.occupied_quantity == count.total_quantity:
        return "Sorry we don't have places for parking"
    if not car:
        await create_car(license_plate, db)
    parking_place = (
        db.query(Parking)
        .filter(Parking.license_plate == license_plate, Parking.status == False)
        .first()
    )

    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    # if user:
    if not parking_place:
        parking_place = await create_parking_place(license_plate, db)
        message = (
            f"Parking successful, please check your email<< {user.email} >> for details"
            if user
            else "Parking successful, to get details please sign up for our Car Parking service"
        )
        parking = _build_parking_schema(parking_place, message=message)
        
        count.occupied_quantity += 1
        db.commit()
        return parking

    parking = _build_parking_schema(
        parking_place,
        message="This car already in parking.",
    )
    return parking


async def exit_from_the_parking(license_plate: str, db: Session):

    user = await repository_users.get_user_by_car_license_plate(license_plate, db)
    # if user:
    parking_place = (
        db.query(Parking)
        .filter(Parking.license_plate == license_plate, Parking.status == False)
        .first()
    )
    if parking_place:
        parking_place = await calculate_invoice(parking_place.id, db)
        departure_time = datetime.now(pytz.timezone("Europe/Kiev"))
        duration = calculate_parking_duration_hours(
            parking_place.enter_time, departure_time
        )
        parking_place.duration = duration
        message = (
            f"Parking invoice sent to your email << {user.email} >>. Please confirm payment"
            if user
            else f"Your parking ID = << {parking_place.id} >>Confirm payment, please."
       )

        parking = _build_parking_schema(
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


async def get_parking_place_by_car_license_plate(
    license_plate: str, db: Session
) -> Parking | None:
    return (
        db.query(Parking)
        .filter(Parking.license_plate == license_plate, Parking.status == False)
        .first()
    )


async def is_valid_file_ext(file: File) -> bool:
    file_ext = file.filename.split(".")[-1]
    if file_ext not in EXTENSIONS:
        return False
    return True

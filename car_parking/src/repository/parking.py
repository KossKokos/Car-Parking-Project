from sqlalchemy.orm import Session
from fastapi import File
# from src.database.models import User, Image
from ..database.models import User, Parking, Car, Parking_count, Tariff
from ..schemas.users import UserModel, UserRoleUpdate, UserParkingResponse, UserResponse
from ..schemas.parking import CurrentParking, ParkingResponse, ParkingInfo, ParkingSchema
from ..repository.car import create_car
# from ..conf.tariffs import STANDART, AUTORIZED
from ..conf.extensions import EXTENSIONS
from ..repository import users as repository_users
from datetime import datetime, timezone
import pytz
from decimal import Decimal


def calculate_datetime_difference(start_time, end_time):
    time_difference = end_time - start_time
    hours = time_difference.days * 24 + time_difference.seconds / 3600
    return round(float(hours), 2)


def calculate_cost(hours, cost):
    result = hours * float(cost)
    return round(result, 2)


async def create_parking_place(license_plate: str, db: Session):
    parking_place = Parking(license_plate=license_plate)

    db.add(parking_place)
    db.commit()
    return parking_place


async def change_parking_status_not_authorised(parking_place_id: int, db: Session):
    parking_place = db.query(Parking).filter(Parking.id == parking_place_id).first()
    user = db.query(User).filter(User.license_plate == parking_place.license_plate).first()
    departure_time = datetime.now(pytz.timezone('Europe/Kiev'))
    duration = calculate_datetime_difference(parking_place.enter_time, departure_time)
    parking_place.status = True
    parking_place.departure_time = departure_time
    parking_place.duration = duration
    count = db.query(Parking_count).first()
    if user:
        tariff = db.query(Tariff).filter_by(id=user.tariff_id).first()
        parking_place.amount_paid = calculate_cost(duration, int(tariff.tariff_value))
    else:
        tariff = db.query(Tariff).filter_by(id=1).first()
        parking_place.amount_paid = calculate_cost(duration, int(tariff.tariff_value))
    parking = ParkingSchema(info=ParkingResponse(
                                    id=parking_place.id,
                                    enter_time=parking_place.enter_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    departure_time=parking_place.departure_time,
                                    license_plate=parking_place.license_plate,
                                    amount_paid=parking_place.amount_paid,
                                    duration=parking_place.duration,
                                    status=False),
                status=f"The barrier is open, See you next time!")
    count.ococcupied_quantity -= 1
    db.commit()
    return parking



async def change_parking_status_authorised(parking_place_id: int, db: Session):
    parking_place = db.query(Parking).filter(Parking.id == parking_place_id).first()
    parking_place.status = True
    count = db.query(Parking_count).first()
    parking_status = ParkingSchema(info=ParkingResponse(
                                            id=parking_place.id,
                                            enter_time=parking_place.enter_time.strftime("%Y-%m-%d %H:%M:%S"),
                                            departure_time=parking_place.departure_time,
                                            license_plate=parking_place.license_plate,
                                            amount_paid=parking_place.amount_paid,
                                            duration=parking_place.duration,
                                            status=False),
                        status=f"The barrier is open, See you next time!")
    count.ococcupied_quantity -= 1
    db.commit()
    return parking_status


async def calculate_invoice(parking_place_id: int, db: Session):
    parking_place = db.query(Parking).filter(Parking.id == parking_place_id).first()
    user = (
        db.query(User).filter(User.license_plate == parking_place.license_plate).first()
    )
    departure_time = datetime.now(pytz.timezone("Europe/Kiev"))
    duration = calculate_datetime_difference(parking_place.enter_time, departure_time)
    parking_place.departure_time = departure_time
    parking_place.duration = duration
    if user:
        tariff = db.query(Tariff).filter_by(id=user.tariff_id).first()
        parking_place.amount_paid = calculate_cost(duration, int(tariff.tariff_value))
    else:
        tariff = db.query(Tariff).filter_by(id=1).first()
        parking_place.amount_paid = calculate_cost(duration, int(tariff.tariff_value))
    db.commit()
    return parking_place


async def entry_to_the_parking(license_plate: str, db: Session):
    car = db.query(Car).filter(Car.license_plate == license_plate).first()

    count = db.query(Parking_count).first()
    if count.ococcupied_quantity == count.total_quantity:
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
        parking = ParkingSchema(
            info=ParkingResponse(
                enter_time=parking_place.enter_time.strftime("%Y-%m-%d %H:%M:%S"),
                departure_time=parking_place.departure_time,
                license_plate=parking_place.license_plate,
                amount_paid=parking_place.amount_paid,
                duration=parking_place.duration,
                status=False,
            ),
            status=f"Parking successful, please check your email<< {user.email} >> for details"
            if user
            else "Parking successful, to get details please sign up for our Car Parking service",
        )
        count.ococcupied_quantity += 1
        db.commit()
        return parking

    parking = ParkingSchema(
        info=ParkingResponse(
            enter_time=parking_place.enter_time.strftime("%Y-%m-%d %H:%M:%S"),
            departure_time=parking_place.departure_time,
            license_plate=parking_place.license_plate,
            amount_paid=parking_place.amount_paid,
            duration=parking_place.duration,
            status=False,
        ),
        status="This car already in parking.",
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
        duration = calculate_datetime_difference(
            parking_place.enter_time, departure_time
        )
        parking_place.duration = duration
        parking = ParkingSchema(
            info=ParkingResponse(
                enter_time=parking_place.enter_time.strftime("%Y-%m-%d %H:%M:%S"),
                departure_time=parking_place.departure_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                license_plate=parking_place.license_plate,
                amount_paid=parking_place.amount_paid,
                duration=parking_place.duration,
                status=False,
            ),
            status=f"Parking invoice sent to your email << {user.email}>>. Please confirm payment"
            if user
            else f"Your parking ID = << {parking_place.id} >>Confirm payment, please.",
        )
        return parking
    return "This car not in parking"


async def seed_parking_count(db: Session):
    if db.query(Parking_count).count() == 0:
        tariffs_data = [
            {"total_quantity": 30, "ococcupied_quantity": 0},
        ]
        for data in tariffs_data:
            tariff = Parking_count(**data)
            db.add(tariff)
        db.commit()
    db.close()


async def free_parking_places(date: str, db: Session):
    date_format = "%Y.%m.%d %H:%M"
    try:
        dt = datetime.strptime(date, date_format)
        kiev_timezone = pytz.timezone("Europe/Kiev")
        dt = kiev_timezone.localize(dt)
        all_parking = db.query(Parking).all()
        quantity = db.query(Parking_count).first()
        all_places = 0
        for parking in all_parking:
            if parking.enter_time <= dt and (
                parking.departure_time is None or dt < parking.departure_time
            ):
                all_places += 1
        free_places = quantity.total_quantity - all_places
        occupied_places = all_places
        return occupied_places
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

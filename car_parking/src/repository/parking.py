from sqlalchemy.orm import Session

# from src.database.models import User, Image
from ..database.models import User, Parking, Car
from ..schemas.users import UserModel, UserRoleUpdate, UserParkingResponse, UserResponse
from ..schemas.parking import CurrentParking, ParkingResponse, ParkingInfo, ParkingSchema
from ..repository.car import create_car
from ..conf.tariffs import STANDART, AUTORIZED
from datetime import datetime, timezone
import pytz


def calculate_datetime_difference(start_time, end_time):
    # end_time = end_time.replace(tzinfo=timezone.utc)
    # start_time = start_time.replace(tzinfo=timezone.utc)
    # end_time = end_time.astimezone(timezone.utc)
    # start_time = start_time.astimezone(timezone.utc)
    time_difference = end_time - start_time
    hours = time_difference.days * 24 + time_difference.seconds / 3600
    return float(hours)


def calculate_cost(hours, cost):
    return hours * cost

async def create_parking_place(license_plate: str, db: Session):
    parking_place = Parking(license_plate=license_plate)

    db.add(parking_place)
    db.commit()
    return parking_place


async def change_parking_status(parking_place_id: int, db: Session):
    parking_place = db.query(Parking).filter(Parking.id == parking_place_id).first()
    user = db.query(User).filter(User.license_plate == parking_place.license_plate).first()
    departure_time = datetime.now(pytz.timezone('Europe/Kiev'))
    duration = calculate_datetime_difference(parking_place.enter_time, departure_time)
    parking_place.status = True
    parking_place.departure_time = departure_time
    parking_place.duration = duration
    if user:
        parking_place.amount_paid = calculate_cost(duration, AUTORIZED)
    else:
        parking_place.amount_paid = calculate_cost(duration, STANDART)
    db.commit()
    return parking_place


async def entry_to_the_parking(license_plate: str, db: Session):
    car = db.query(Car).filter(Car.license_plate == license_plate).first()
    if not car:
        await create_car(license_plate, db)
    parking_place = db.query(Parking).filter(Parking.license_plate == license_plate, Parking.status == False).first()
    if not parking_place:
        parking_place = await create_parking_place(license_plate, db)
        parking = ParkingSchema(info=ParkingResponse(enter_time=parking_place.enter_time,
                                                     departure_time=parking_place.departure_time,
                                                     license_plate=parking_place.license_plate,
                                                     amount_paid=parking_place.amount_paid,
                                                     duration=parking_place.duration,
                                                     status=False),
                                #status="You can park."
                                status = "Parking successfull, please check your email for details")
        return parking
    parking = ParkingSchema(info=ParkingResponse(enter_time=parking_place.enter_time,
                                                 departure_time=parking_place.departure_time,
                                                 license_plate=parking_place.license_plate,
                                                 amount_paid=parking_place.amount_paid,
                                                 duration=parking_place.duration,
                                                 status=False),
                            status="This car already in parking.")
    return parking


async def exit_from_the_parking(license_plate: str, db: Session):
    parking_place = (
        db.query(Parking)
        .filter(Parking.license_plate == license_plate, Parking.status == False)
        .first()
    )
    if parking_place:
        parking_place = await change_parking_status(parking_place.id, db)
        parking = ParkingSchema(
            info=ParkingResponse(
                enter_time=parking_place.enter_time,
                departure_time=parking_place.departure_time,
                license_plate=parking_place.license_plate,
                amount_paid=parking_place.amount_paid,
                duration=parking_place.duration,
                status=False,
            ),
            status="You can go.",
        )
        return parking
    return "This car not in parking"

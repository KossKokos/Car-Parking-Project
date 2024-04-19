import pytz
from sqlalchemy.orm import Session
from car_parking.src.database.models import User, Parking, Tariff, Car
from car_parking.src.schemas.users import (
    UserModel,
    UserParkingResponse,
    UserResponse,
)
from car_parking.src.schemas.parking import CurrentParking, ParkingResponse, ParkingInfo
from datetime import datetime


def calculate_datetime_difference(start_time, end_time):
    time_difference = end_time - start_time
    hours = time_difference.days * 24 + time_difference.seconds / 3600
    return round(float(hours), 2)


def calculate_cost(hours, cost):
    result = hours * float(cost)
    return round(result, 2)


async def create_user(body: UserModel, db: Session) -> User:
    user = User(**body.dict())
    print(body)
    user.license_plate = body.license_plate.upper()
    user.tariff_id = 2
    db.add(user)
    db.commit()
    if user.id == 1:
        user.role = "admin"
        db.commit()
    db.refresh(user)
    return user


async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


async def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).filter(User.username == username).first()


async def update_token(user: User, refresh_token: str, db: Session) -> None:
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def change_password(user: User, new_password: str, db: Session) -> None:
    user.password = new_password
    db.commit()
    db.refresh(user)


async def get_user_by_id(user_id: int, db: Session) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


async def delete_user(user_id: int, db: Session) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return None


async def get_user_by_car_license_plate(
    license_plate: str, db: Session
) -> User | None:
    license_plate = license_plate.upper()
    user = db.query(User).filter_by(license_plate=license_plate).first()
    return user


async def calculate_amount_cost(list_of_parking: list[list[Parking]]):
    total_cost = 0
    for park in list_of_parking:
        total_cost += park.amount_paid
    return total_cost


async def calculate_amount_duration(list_of_parking: list[list[Parking]]):
    total_duration = 0
    for park in list_of_parking:
        total_duration += park.duration
    return total_duration


async def get_parking_info(license_plate: str, db: Session):
    user = await get_user_by_car_license_plate(license_plate, db)
    license_plate = license_plate.upper()
    car = db.query(Car).filter(Car.license_plate == license_plate).first()
    if not car:
        return "This car is not registered"
    parking_info = (
        db.query(Parking)
        .filter(Parking.license_plate == license_plate, Parking.status == True)
        .all()
    )
    total_payment_amount = await calculate_amount_cost(parking_info)
    total_parking_time = await calculate_amount_duration(parking_info)
    parking_history = ParkingInfo(
        user=user.username if user else "Unregister user",
        total_payment_amount=total_payment_amount,
        total_parking_time=total_parking_time,
        parking_info=[],
    )
    for parking in parking_info:
        parking_history.parking_info.append(
            ParkingResponse(
                id=parking.id,
                enter_time=parking.enter_time.strftime("%Y-%m-%d %H:%M:%S"),
                departure_time=parking.departure_time.strftime("%Y-%m-%d %H:%M:%S"),
                license_plate=parking.license_plate,
                amount_paid=parking.amount_paid,
                duration=parking.duration,
                status=parking.status,
            )
        )
    return parking_history


async def get_user_me(user: User, db: Session):
    user_parking = (
        db.query(Parking)
        .filter(Parking.license_plate == user.license_plate, Parking.status == False)
        .first()
    )
    tariff = db.query(Tariff).filter_by(id=user.tariff_id).first()
    if user_parking:
        time_on_parking = calculate_datetime_difference(
            user_parking.enter_time, datetime.now(pytz.timezone("Europe/Kiev"))
        )
        current_cost = calculate_cost(time_on_parking, tariff.tariff_value)

        user_park = UserParkingResponse(
            user=UserResponse(
                id=user.id,
                usernam=user.username,
                email=user.email,
                license_plate=user.license_plate,
                banned=user.banned,
                role=user.role
                
            ),
            parking=CurrentParking(
                license_plate=user.license_plate,
                enter_time=user_parking.enter_time.strftime("%Y-%m-%d %H:%M:%S"),
                time_on_parking=time_on_parking,
                parking_cost=current_cost,
            ),
        )
        return user_park
    user_park = UserParkingResponse(
        user=UserResponse(
            id=user.id,
            username=user.username, 
            email=user.email, 
            license_plate=user.license_plate,
            banned=user.banned,
            role=user.role
        ),
        parking="You don't have a car parked right now.",
    )
    return user_park

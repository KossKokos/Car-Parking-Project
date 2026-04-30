from datetime import datetime

import pytz
from sqlalchemy.orm import Session

from car_parking.src.conf.constants import DEFAULT_USER_TARIFF_ID, ADMIN_USER_ID, RESPONSE_DATETIME_FORMAT
from car_parking.src.database.models import Car, Parking, Tariff, User
from car_parking.src.schemas.parking import CurrentParking, ParkingInfo, ParkingResponse
from car_parking.src.schemas.users import (
    UserModel,
    UserParkingResponse,
    UserResponse,
)
from car_parking.src.utils.users_helpers import _format_datetime_for_response, _get_car_by_license_plate, _get_closed_parking_sessions_by_license_plate, _get_current_parking_session_by_license_plate, _normalize_license_plate, calculate_amount_cost, calculate_amount_duration

from ..services.parking_calculations import (
    calculate_parking_cost,
    calculate_parking_duration_hours,
)


async def create_user(body: UserModel, db: Session) -> User:
    user = User(**body.dict())
    user.license_plate = _normalize_license_plate(body.license_plate)
    user.tariff_id = DEFAULT_USER_TARIFF_ID

    db.add(user)
    db.commit()

    if user.id == ADMIN_USER_ID:
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
    license_plate: str,
    db: Session,
) -> User | None:
    return db.query(User).filter_by(
        license_plate=_normalize_license_plate(license_plate)
    ).first()


async def get_parking_info(license_plate: str, db: Session):
    normalized_license_plate = _normalize_license_plate(license_plate)

    user = await get_user_by_car_license_plate(normalized_license_plate, db)
    car = _get_car_by_license_plate(normalized_license_plate, db)

    if not car:
        return "This car is not registered"

    parking_info = _get_closed_parking_sessions_by_license_plate(
        normalized_license_plate,
        db,
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
                enter_time=_format_datetime_for_response(parking.enter_time),
                departure_time=_format_datetime_for_response(parking.departure_time),
                license_plate=parking.license_plate,
                amount_paid=parking.amount_paid,
                duration=parking.duration,
                status=parking.status,
            )
        )
    return parking_history


async def get_user_me(user: User, db: Session):
    user_parking = _get_current_parking_session_by_license_plate(
        user.license_plate,
        db,
    )
    tariff = db.query(Tariff).filter_by(id=user.tariff_id).first()
    if user_parking:
        time_on_parking = calculate_parking_duration_hours(
            user_parking.enter_time, datetime.now(pytz.timezone("Europe/Kiev"))
        )
        current_cost = calculate_parking_cost(time_on_parking, tariff.tariff_value)

        user_park = UserParkingResponse(
            user=UserResponse(
                username=user.username,
                email=user.email,
                license_plate=user.license_plate,
            ),
            parking=CurrentParking(
                enter_time=_format_datetime_for_response(user_parking.enter_time),
                time_on_parking=time_on_parking,
                parking_cost=current_cost,
            ),
        )
        return user_park
    user_park = UserParkingResponse(
        user=UserResponse(
            username=user.username, email=user.email, license_plate=user.license_plate
        ),
        parking="You don't have a car parked right now.",
    )
    return user_park

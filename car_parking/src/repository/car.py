from sqlalchemy.orm import Session

from car_parking.src.database.models import Car


async def create_car(license_plate, db: Session) -> Car:
    license_plate = license_plate.upper()
    car = Car(license_plate=license_plate)
    db.add(car)
    db.commit()
    return car


async def get_car_by_license_plate(license_plate: str, db: Session) -> Car | None:
    return db.query(Car).filter(Car.license_plate == license_plate).first()


async def set_car_banned_status(
    car: Car,
    is_banned: bool,
    db: Session,
) -> Car:
    car.banned = is_banned
    db.commit()
    db.refresh(car)
    return car

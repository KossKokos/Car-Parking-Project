from sqlalchemy.orm import Session

# from src.database.models import User, Image
from ..database.models import User, Parking, Car
from ..schemas.users import UserModel


async def create_car(license_plate, db: Session) -> Car:
    license_plate = license_plate.upper()
    car = Car(license_plate=license_plate)
    db.add(car)
    db.commit()
    return car

async def get_car_by_license_plate(license_plate, db: Session) -> Car:
    return db.query(Car).filter(Car.license_plate==license_plate).first()

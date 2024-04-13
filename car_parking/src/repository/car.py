from sqlalchemy.orm import Session

from ..database.models import Car



async def create_car(license_plate, db: Session) -> Car:
    license_plate = license_plate.upper()
    car = Car(license_plate=license_plate)
    db.add(car)
    db.commit()
    return car

async def get_car_by_license_plate(license_plate, db: Session) -> Car:
    return db.query(Car).filter(Car.license_plate==license_plate).first()

from sqlalchemy.orm import Session

from ..database.models import Car
from ..schemas.users import UserModel, UserRoleUpdate



async def get_car_by_license_plate(license_plate: str, db: Session) -> Car | None:

    return db.query(Car).filter(Car.license_plate==license_plate).first()

async def update_car_banned_status(car: Car, db: Session):
    
    car.banned = True
    db.commit()
    db.refresh(car)
    return car

async def update_car_unbanned_status(car: Car, db: Session):

    car.banned = False
    db.commit()
    db.refresh(car)
    return car
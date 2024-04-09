from sqlalchemy.orm import Session

# from src.database.models import User, Image
from ..database.models import User, Parking, Car
from ..schemas.users import UserModel


async def create_car(license_plate, db: Session) -> User:
    car = Car(license_plate=license_plate)
    db.add(car)
    db.commit()
    return car

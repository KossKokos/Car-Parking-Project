from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..database.models import User
from ..database import db

from sqlalchemy.orm import Session
from ..database.models import Car, User

import sys
from pathlib import Path
path = str(Path(__file__).parent.parent.parent)
sys.path.append(path)


class AdminService:
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        return user

    def update_user(self, db: Session, user_id: int, new_data: dict) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        for key, value in new_data.items():
            setattr(user, key, value)
        try:
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
        
    def get_all_users(self, db: Session) -> List[User]:
        users = db.query(User).all()
        return 
    
    def get_cars_with_user_by_car_number(self, db: Session, car_number: str):
        car = db.query(Car).filter(Car.number == car_number).first()
        if car:
            user = db.query(User).filter(User.car_id == car.id).first()
            return car, user
        else:
            return None, None


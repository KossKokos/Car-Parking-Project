from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import db
from src.repository.AdminService import AdminService
from ..database.models import User
from ..database import get_db

router = APIRouter()
admin_service = AdminService()

@router.get("/admin/users")
def get_all_users(db: Session = Depends(get_db)):
    admin_service = AdminService()
    users = admin_service.get_all_users(db)
    return users

@router.put("/admin/users/{user_id}")
async def admin_update_user(user_id: int, new_data: dict, db: Session = Depends(db.get_db)):
    admin_service = AdminService()
    if admin_service.update_user(db, user_id, new_data):
        return {"message": "User information updated successfully"}
    else:
        return {"message": "Failed to update user information"}
    
@router.get("/admin/cars")
def get_cars_with_user_by_car_number(car_number: str, db: Session = Depends(get_db)):
    car, user = admin_service.get_cars_with_user_by_car_number(db, car_number)
    if car:
        if user:
            return {"car": car, "user": user}
        else:
            return {"car": car}
    else:
        return {"message": "Car not found"}

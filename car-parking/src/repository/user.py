from typing import Type
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
import sys
sys.path.append("/../car-parking/src")
from database.models import User 

async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter_by(email=email).first()

async def admin_edit_user(user_id, new_data):  
    user_service = UserService()  
    user_info = await get_user_by_email(user_id)
    if user_info:
        user_service.update_user(user_id, new_data)
        print("Інформація про користувача успішно оновлена.")
    else:
        print("Користувача з таким ID не знайдено.")


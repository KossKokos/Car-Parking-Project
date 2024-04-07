from AdminService import AdminService
from typing import Type
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
import sys
from pathlib import Path
path = str(Path(__file__).parent.parent.parent)
sys.path.append(path)

from src.database.models import User  

async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter_by(email=email).first()

async def admin_edit_user(user_id, new_data):  
    admin_service = AdminService()  
    user_info = await get_user_by_email(user_id)
    if user_info:
        admin_service.update_user(user_id, new_data)  
        print("Інформація про користувача успішно оновлена.")
    else:
        print("Користувача з таким ID не знайдено.")


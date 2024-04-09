from sqlalchemy.orm import Session

from ..database.models import User
from ..schemas.users import UserModel


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        

    :param body: UserModel: Deserialize the request body into a usermodel object
    :param db: Session: Access the database
    :return: A user object
    """
    user = User(**body.dict())
    db.add(user)
    db.commit()
    if user.id == 1:
        user.role = "admin"
        db.commit()
    db.refresh(user)
    return user


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Specify the email of the user we want to get from our database
    :param db: Session: Pass the database session to the function
    :return: A user object or none if the user is not found
    """
    return db.query(User).filter(User.email==email).first()


async def get_user_by_username(username: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Specify the email of the user we want to get from our database
    :param db: Session: Pass the database session to the function
    :return: A user object or none if the user is not found
    """
    return db.query(User).filter(User.username==username).first()

async def update_token(user: User, refresh_token: str, db: Session) -> None:
    """
    The update_token function updates the refresh_token for a user in the database.
        Args:
            user (User): The User object to update.
            refresh_token (str): The new refresh token to store in the database.
            db (Session): A SQLAlchemy Session object used to interact with the database.
    
    :param user: User: Get the user's object from the database
    :param refresh_token: Update the refresh_token in the database
    :param db: Session: Access the database
    :return: None
    """
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.
    
    :param email: str: Get the email address of the user
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def change_password(user: User, new_password: str, db: Session) -> None:
    """
    The change_password function changes the password of a user.
    
    Args:
        user (User): The User object to change the password for.
        new_password (str): The new password to set for this user.
        db (Session): A database session object.
    
    :param user: User: Specify the user whose password is to be changed
    :param new_password: str: Change the password of a user
    :param db: Session: Pass in the database session
    :return: None
    """
    user.password = new_password
    db.commit()
    db.refresh(user)


async def get_user_by_id(user_id: int, db: Session) -> User | None:
    """
    The get_user_by_id function returns a User object from the database, given an id.
        Args:
            user_id (int): The id of the user to be retrieved.
            db (Session): A Session instance for interacting with the database.
    
    :param user_id: int: Specify the type of parameter that is expected to be passed in
    :param db: Session: Pass the database session to the function
    :return: A user object or none
    :doc-author: Trelent
    """
    return db.query(User).filter(User.id==user_id).first()
    
    
async def delete_user(user_id: int, db: Session) -> None:
    """
    The delete_user function deletes a user from the database based on the user ID.

    :param user_id: int: ID of the user to be deleted
    :param db: Session: Database session
    :return: None
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return None 


async def get_user_by_car_license_plate(license_plate: str, db: Session) -> User | None:
    return db.query(User).filter(User.license_plate==license_plate).first()








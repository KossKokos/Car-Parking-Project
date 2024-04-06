from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func, CheckConstraint, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import DateTime


Base = declarative_base()

"""User:
    name = ...
    password =
    email = ...
    plate_number.id = foreign_key(Car)
    role = ...
    tariff = enum
    # max_limit"""


class User(Base):
    __tablename__ = "users_table"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(String(20), nullable=False, default='user')
    license_plate = Column('lcense_plate', ForeignKey('cars_table.license_plate', ondelete='CASCADE'), unique=True)
    blacklisted_token = relationship('BlacklistedToken', uselist=False, back_populates='user')
    cars = relationship('Car', uselist=True, back_populates='user')

    __table_args__ = (
        CheckConstraint(
            role.in_(['admin', 'user']),
            name='check_valid_role'
        ),
    )

    def __str__(self):
        return str(self.id)

"""
parking:
    enter_time = ...
    exit_time = ...
    Car = foreign_key(Car)
    status = enum
    duration = exit_time - enter_time (minutes)
    amount_paid = ...
"""

class Parking(Base):
    __tablename__ = "parking_places_table"

    id = Column(Integer, primary_key=True)
    enter_time = Column(DateTime(timezone=True), server_default=func.now())
    departure_time = Column(DateTime(timezone=True))
    places_quantity = Column(Integer)
    status = Column(Boolean, default=False) #Free -false / true - occupated
    license_plate = Column('lcense_plate', ForeignKey('cars_table.license_plate', ondelete='CASCADE'))
    amount_paid = Column(float)
    duration = Column(float)
    car = relationship("Car", uselist=False, back_populates="parking_place")

"""
# Define an event listener to automatically update exit_time
@event.listens_for(Parking.car, 'remove')
def update_exit_time(target, value, oldvalue, initiator):
    if value is not None:
        target.exit_time = func.now()
"""

class Car(Base):
    __tablename__ = 'cars_table'

    id = Column(Integer, primary_key=True)
    license_plate = Column(String(30), nullable=False, unique=True)
    banned = Column(Boolean, default=False)
    user = relationship('User', uselist=False, back_populates='cars')
    parking_place = relationship("Parking", uselist=False,  back_populates="car")
    

class BlacklistedToken(Base):
    __tablename__ = 'blacklisted_tokens'

    id = Column(Integer, primary_key=True)
    blacklisted_token = Column(String(255), nullable=True)
    user_id = Column('user_id', ForeignKey('users_table.id', ondelete='CASCADE'), unique=True)
    user = relationship('User', back_populates='blacklisted_token')

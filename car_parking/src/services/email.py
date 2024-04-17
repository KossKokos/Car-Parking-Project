from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from car_parking.src.services.auth import service_auth
from car_parking.src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Car parking",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str) -> None:
    try:
        token_verification = await service_auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(email: EmailStr, username: str, host: str) -> None:
    try:
        token_verification = await service_auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Reset password ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)


async def praking_enter_message(
    email: EmailStr,
    username: str,
    license_plate: str,
    enter_time,
    tariff_name,
    tariff_value,
    host: str,
) -> None:
    try:
        token_verification = await service_auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Parking place info",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "license_plate": license_plate,
                "enter_time": enter_time,
                "tariff_name": tariff_name,
                "tariff_value": tariff_value,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="praking_enter_message.html")
    except ConnectionErrors as err:
        print(err)


# original code
# async def praking_exit_message(email: EmailStr,
#                                username: str,
#                                license_plate:str,
#                                enter_time,
#                                tariff_name,
#                                tariff_value,
#                                host: str) -> None:

#     try:
#         token_verification = await service_auth.create_email_token({"sub": email})
#         message = MessageSchema(
#             subject="Invoice for payment",
#             recipients=[email],
#             template_body={"host": host,
#                            "username": username,
#                            "license_plate": license_plate,
#                            "enter_time" :enter_time,
#                            "tariff_name": tariff_name,
#                            "tariff_value": tariff_value,
#                            "token": token_verification},
#             subtype=MessageType.html
#         )

#         fm = FastMail(conf)
#         await fm.send_message(message, template_name="praking_exit_message.html")
#     except ConnectionErrors as err:
#         print(err)


# second version
async def praking_exit_message(
    email: EmailStr,
    username: str,
    license_plate: str,
    parking_place_id,
    enter_time,
    departure_time,
    tariff_name,
    tariff_value,
    duration,
    amount_paid,
    host: str,
) -> None:
    try:
        token_verification = await service_auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Invoice for payment",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "license_plate": license_plate,
                "parking_place_id": parking_place_id,
                "enter_time": enter_time,
                "departure_time": departure_time,
                "tariff_name": tariff_name,
                "tariff_value": tariff_value,
                "duration": duration,
                "amount_paid": amount_paid,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="praking_exit_message.html")
    except ConnectionErrors as err:
        print(err)

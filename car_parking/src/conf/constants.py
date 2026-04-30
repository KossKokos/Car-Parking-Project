# repository/parking
PARKING_COUNT_DATA = [
            {"total_quantity": 30, "occupied_quantity": 0},
        ]

TARIFFS_DATA = [
            {"tariff_name": "STANDART", "tariff_value": 30},
            {"tariff_name": "AUTORIZED", "tariff_value": 20},
            {"tariff_name": "MAX_LIMIT", "tariff_value": 1000},
        ]
RESPONSE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TARIFF_ID = 1

# repository/users
DEFAULT_USER_TARIFF_ID = 2
ADMIN_USER_ID = 1

# routes/parking
LICENSE_PLATE_NOT_FOUND_MESSAGE = (
    "License plate not found, please send better picture where car is visible"
)
PARKING_AVAILABILITY_DATETIME_FORMAT = "%Y.%m.%d %H:%M"
TIMEZONE = "Europe/London"
from sqlalchemy.orm import Session

from car_parking.src.database.models import Tariff


async def get_tariff_by_tariff_id(tariff_id: int, db: Session) -> Tariff | None:
    tariff = db.query(Tariff).filter(Tariff.id == tariff_id).first()
    return tariff


async def seed_tariff_table(db: Session):
    # Check if the Tariff table is empty
    if db.query(Tariff).count() == 0:
        # Define data for three tariffs

        tariffs_data = [
            {"tariff_name": "STANDART", "tariff_value": 30},
            {"tariff_name": "AUTORIZED", "tariff_value": 20},
            {"tariff_name": "MAX_LIMIT", "tariff_value": 1000},
        ]

        # Add the tariffs to the database
        for data in tariffs_data:
            tariff = Tariff(**data)
            db.add(tariff)

        # Commit the changes
        db.commit()

        print("Tariffs added successfully!")
    else:
        print("Tariff table is not empty. Data not added.")

    # Close the session
    db.close()

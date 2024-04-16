from sqlalchemy.orm import Session

from car_parking.src.database.models import Tariff


async def get_tariff_by_tariff_id(tariff_id: int, db: Session) -> Tariff | None:
    tariff = db.query(Tariff).filter(Tariff.id == tariff_id).first()
    return tariff


async def seed_tariff_table(db: Session):
    if db.query(Tariff).count() == 0:
        tariffs_data = [
            {"tariff_name": "STANDART", "tariff_value": 30},
            {"tariff_name": "AUTORIZED", "tariff_value": 20},
            {"tariff_name": "MAX_LIMIT", "tariff_value": 1000},
        ]

        for data in tariffs_data:
            tariff = Tariff(**data)
            db.add(tariff)
        db.commit()
    db.close()

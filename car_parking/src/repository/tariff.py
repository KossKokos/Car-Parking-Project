from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database.models import Tariff


async def get_tariff_by_tariff_id(tariff_id: int, db: Session) -> Tariff | None:
    tariff = db.query(Tariff).filter(Tariff.id==tariff_id).first()
    print (tariff.id)
    return tariff



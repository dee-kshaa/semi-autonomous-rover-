from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.operator import Operator
from app.models.signal_log import SignalLog
from app.schemas.signal import SignalLogCreate


class SignalService:
    COORDINATE_PRECISION = 5

    @staticmethod
    def create_signal_log(db: Session, user_id: int, payload: SignalLogCreate) -> SignalLog:
        rounded_latitude = round(payload.latitude, SignalService.COORDINATE_PRECISION)
        rounded_longitude = round(payload.longitude, SignalService.COORDINATE_PRECISION)

        operator = db.query(Operator).filter(func.lower(Operator.name) == payload.operator_name.lower()).first()
        if not operator:
            operator = Operator(name=payload.operator_name)
            db.add(operator)
            db.flush()

        location = (
            db.query(Location)
            .filter(
                Location.latitude == rounded_latitude,
                Location.longitude == rounded_longitude,
            )
            .first()
        )
        if not location:
            location = Location(latitude=rounded_latitude, longitude=rounded_longitude, city=payload.city)
            db.add(location)
            db.flush()
        elif not location.city and payload.city:
            location.city = payload.city
            db.flush()

        log = SignalLog(
            user_id=user_id,
            location_id=location.id,
            operator_id=operator.id,
            rssi=payload.rssi,
            network_type=payload.network_type,
            device_model=payload.device_model,
            device_os=payload.device_os,
            recorded_at=payload.timestamp,
            speed_mps=payload.speed_mps,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

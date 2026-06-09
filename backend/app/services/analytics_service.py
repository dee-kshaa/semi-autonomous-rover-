from datetime import datetime, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.operator import Operator
from app.models.prediction import Prediction
from app.models.signal_log import SignalLog
from app.models.user import User


class AnalyticsService:
    @staticmethod
    def summary(db: Session) -> dict:
        total_samples = db.query(func.count(SignalLog.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).scalar() or 0
        avg_rssi = db.query(func.avg(SignalLog.rssi)).scalar() or 0.0

        quality_case = case(
            (SignalLog.rssi >= -70, 'excellent'),
            (SignalLog.rssi >= -85, 'good'),
            (SignalLog.rssi >= -100, 'fair'),
            else_='poor',
        ).label('quality')

        rows = db.query(quality_case, func.count(SignalLog.id)).group_by(quality_case).all()
        quality_distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        for label, count in rows:
            quality_distribution[label] = count

        return {
            'total_samples': int(total_samples),
            'active_users': int(active_users),
            'avg_rssi': float(avg_rssi),
            'quality_distribution': quality_distribution,
        }

    @staticmethod
    def trend(db: Session, hours: int = 24) -> list[dict]:
        start = datetime.utcnow() - timedelta(hours=hours)
        rows = (
            db.query(
                func.date_trunc('hour', SignalLog.recorded_at).label('bucket'),
                func.avg(SignalLog.rssi).label('avg_rssi'),
            )
            .filter(SignalLog.recorded_at >= start)
            .group_by('bucket')
            .order_by('bucket')
            .all()
        )
        return [{'bucket': str(r.bucket), 'avg_rssi': float(r.avg_rssi)} for r in rows]

    @staticmethod
    def operator_comparison(db: Session) -> list[dict]:
        rows = (
            db.query(
                Operator.name,
                func.avg(SignalLog.rssi).label('avg_rssi'),
                func.count(SignalLog.id).label('samples'),
                func.avg(case((Prediction.dead_zone_probability >= 0.5, 1), else_=0)).label('dead_zone_prediction_rate'),
            )
            .join(SignalLog, SignalLog.operator_id == Operator.id)
            .outerjoin(Prediction, Prediction.signal_log_id == SignalLog.id)
            .group_by(Operator.name)
            .all()
        )

        return [
            {
                'operator_name': row.name,
                'avg_rssi': float(row.avg_rssi),
                'sample_count': int(row.samples),
                'dead_zone_rate': float(row.dead_zone_prediction_rate or 0.0),
            }
            for row in rows
        ]

    @staticmethod
    def heatmap(db: Session) -> list[dict]:
        rows = (
            db.query(
                Location.latitude,
                Location.longitude,
                func.avg(SignalLog.rssi).label('avg_rssi'),
                func.count(SignalLog.id).label('samples'),
            )
            .join(SignalLog, SignalLog.location_id == Location.id)
            .group_by(Location.latitude, Location.longitude)
            .all()
        )
        return [
            {
                'latitude': float(row.latitude),
                'longitude': float(row.longitude),
                'avg_rssi': float(row.avg_rssi),
                'sample_count': int(row.samples),
            }
            for row in rows
        ]

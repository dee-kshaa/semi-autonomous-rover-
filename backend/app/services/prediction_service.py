from app.models.prediction import Prediction
from app.models.signal_log import SignalLog
from sqlalchemy.orm import Session

ANOMALY_BASELINE_RSSI = -85
ANOMALY_NORMALIZER = 60.0


class PredictionService:
    @staticmethod
    def _coverage_class_from_rssi(rssi: int) -> str:
        if rssi >= -70:
            return 'excellent'
        if rssi >= -85:
            return 'good'
        if rssi >= -100:
            return 'fair'
        return 'poor'

    @staticmethod
    def infer_and_store(db: Session, signal_log: SignalLog) -> Prediction:
        predicted_signal = float(signal_log.rssi + 2)
        dead_zone_probability = 0.8 if signal_log.rssi < -105 else 0.2
        coverage_class = PredictionService._coverage_class_from_rssi(signal_log.rssi)
        anomaly_score = abs(signal_log.rssi - ANOMALY_BASELINE_RSSI) / ANOMALY_NORMALIZER

        prediction = Prediction(
            signal_log_id=signal_log.id,
            predicted_signal_strength=predicted_signal,
            dead_zone_probability=dead_zone_probability,
            recommended_operator=signal_log.operator.name,
            coverage_class=coverage_class,
            anomaly_score=anomaly_score,
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

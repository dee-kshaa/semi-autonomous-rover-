from __future__ import annotations

import numpy as np

from ml_models.anomaly_detection import SignalAnomalyDetector
from ml_models.dead_zone_classifier import DeadZoneClassifier
from ml_models.operator_recommendation import OperatorRecommendationModel
from ml_models.signal_strength_prediction import SignalStrengthPredictionModel


def run_inference(
    signal_model: SignalStrengthPredictionModel,
    dead_zone_model: DeadZoneClassifier,
    anomaly_model: SignalAnomalyDetector,
    operator_model: OperatorRecommendationModel,
    features: np.ndarray,
) -> list[dict]:
    predicted_signal = signal_model.predict(features)
    dead_zone_probability = dead_zone_model.predict_proba(features)[:, 1]
    anomaly_score = anomaly_model.anomaly_score(features)
    operator, operator_confidence = operator_model.recommend_with_confidence(features)

    return [
        {
            "predicted_signal_strength": float(predicted_signal[i]),
            "dead_zone_probability": float(dead_zone_probability[i]),
            "anomaly_score": float(anomaly_score[i]),
            "recommended_operator": str(operator[i]),
            "operator_confidence": float(operator_confidence[i]),
        }
        for i in range(len(features))
    ]

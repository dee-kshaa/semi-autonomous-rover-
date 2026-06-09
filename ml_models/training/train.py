from __future__ import annotations

import numpy as np

from ml_models.anomaly_detection import SignalAnomalyDetector
from ml_models.dead_zone_classifier import DeadZoneClassifier
from ml_models.operator_recommendation import OperatorRecommendationModel
from ml_models.signal_strength_prediction import SignalStrengthPredictionModel


def train_models(
    features: np.ndarray,
    rssi_targets: np.ndarray,
    operator_targets: np.ndarray,
) -> tuple[
    SignalStrengthPredictionModel,
    DeadZoneClassifier,
    SignalAnomalyDetector,
    OperatorRecommendationModel,
]:
    signal_model = SignalStrengthPredictionModel().fit(features, rssi_targets)
    dead_zone_labels = DeadZoneClassifier.derive_labels_from_rssi(rssi_targets)
    dead_zone_model = DeadZoneClassifier().fit(features, dead_zone_labels)
    anomaly_model = SignalAnomalyDetector().fit(features)
    operator_model = OperatorRecommendationModel().fit(features, operator_targets)
    return signal_model, dead_zone_model, anomaly_model, operator_model

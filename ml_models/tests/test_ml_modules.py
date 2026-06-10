import numpy as np

from ml_models.anomaly_detection import SignalAnomalyDetector
from ml_models.dead_zone_classifier import DeadZoneClassifier
from ml_models.inference.predict import run_inference
from ml_models.operator_recommendation import OperatorRecommendationModel
from ml_models.signal_strength_prediction import SignalStrengthPredictionModel
from ml_models.training.train import train_models


def _sample_data():
    rng = np.random.default_rng(42)
    features = rng.normal(0, 1, size=(60, 4))
    rssi = -85 + features[:, 0] * 6 - features[:, 1] * 3
    operator = np.where(features[:, 2] > 0.3, "OperatorA", "OperatorB")
    return features, rssi, operator


def test_training_pipeline_outputs_models():
    features, rssi, operator = _sample_data()
    signal_model, dead_zone_model, anomaly_model, operator_model = train_models(features, rssi, operator)
    assert isinstance(signal_model, SignalStrengthPredictionModel)
    assert isinstance(dead_zone_model, DeadZoneClassifier)
    assert isinstance(anomaly_model, SignalAnomalyDetector)
    assert isinstance(operator_model, OperatorRecommendationModel)


def test_inference_output_shape():
    features, rssi, operator = _sample_data()
    signal_model, dead_zone_model, anomaly_model, operator_model = train_models(features, rssi, operator)
    results = run_inference(signal_model, dead_zone_model, anomaly_model, operator_model, features[:5])
    assert len(results) == 5
    assert "predicted_signal_strength" in results[0]
    assert "recommended_operator" in results[0]


def test_dead_zone_label_derivation():
    labels = DeadZoneClassifier.derive_labels_from_rssi(np.array([-90, -106, -120]))
    assert labels.tolist() == [0, 1, 1]

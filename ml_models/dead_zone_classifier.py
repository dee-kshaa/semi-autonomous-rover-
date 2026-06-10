from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestClassifier

DEAD_ZONE_RSSI_THRESHOLD = -105


@dataclass(slots=True)
class DeadZoneClassifier:
    n_estimators: int = 120
    random_state: int = 42

    def __post_init__(self) -> None:
        self._model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            class_weight="balanced",
            n_jobs=-1,
        )

    @staticmethod
    def derive_labels_from_rssi(rssi: np.ndarray) -> np.ndarray:
        return (rssi <= DEAD_ZONE_RSSI_THRESHOLD).astype(int)

    def fit(self, features: np.ndarray, labels: np.ndarray) -> "DeadZoneClassifier":
        self._model.fit(features, labels)
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        return self._model.predict(features)

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        return self._model.predict_proba(features)

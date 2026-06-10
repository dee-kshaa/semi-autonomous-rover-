from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass(slots=True)
class SignalAnomalyDetector:
    contamination: float = 0.05
    random_state: int = 42

    def __post_init__(self) -> None:
        self._model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
        )

    def fit(self, features: np.ndarray) -> "SignalAnomalyDetector":
        self._model.fit(features)
        return self

    def anomaly_score(self, features: np.ndarray) -> np.ndarray:
        return -self._model.score_samples(features)

    def is_anomaly(self, features: np.ndarray, threshold: float | None = None) -> np.ndarray:
        scores = self.anomaly_score(features)
        score_threshold = threshold if threshold is not None else float(np.quantile(scores, 0.95))
        return scores >= score_threshold

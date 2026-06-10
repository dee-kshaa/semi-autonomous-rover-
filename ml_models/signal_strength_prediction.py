from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestRegressor


@dataclass(slots=True)
class SignalStrengthPredictionModel:
    n_estimators: int = 100
    random_state: int = 42

    def __post_init__(self) -> None:
        self._model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1,
        )

    def fit(self, features: np.ndarray, targets: np.ndarray) -> "SignalStrengthPredictionModel":
        self._model.fit(features, targets)
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        return self._model.predict(features)

    def score(self, features: np.ndarray, targets: np.ndarray) -> float:
        return float(self._model.score(features, targets))

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression


@dataclass(slots=True)
class OperatorRecommendationModel:
    random_state: int = 42

    def __post_init__(self) -> None:
        self._model = LogisticRegression(
            random_state=self.random_state,
            max_iter=1000,
            multi_class="multinomial",
        )

    def fit(self, features: np.ndarray, operators: np.ndarray) -> "OperatorRecommendationModel":
        self._model.fit(features, operators)
        return self

    def recommend(self, features: np.ndarray) -> np.ndarray:
        return self._model.predict(features)

    def recommend_with_confidence(self, features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        probabilities = self._model.predict_proba(features)
        max_index = np.argmax(probabilities, axis=1)
        labels = self._model.classes_[max_index]
        confidence = probabilities[np.arange(len(max_index)), max_index]
        return labels, confidence

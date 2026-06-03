from __future__ import annotations

import json
import math
from pathlib import Path


MODEL_PATH = Path(__file__).with_name("ufo-model.json")
COUNTRY_CODES = {
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "United Kingdom": "gb",
    "United States": "us",
}


class UfoLinearSoftmaxModel:
    def __init__(self, payload: dict[str, object]) -> None:
        self.labels = payload["labels"]
        self.scaler = payload["scaler"]
        self.coefficients = payload["coefficients"]
        self.intercepts = payload["intercepts"]
        self.metadata = payload.get("metadata", {})

    @classmethod
    def load(cls, path: Path = MODEL_PATH) -> "UfoLinearSoftmaxModel":
        with path.open("r", encoding="utf-8") as model_file:
            return cls(json.load(model_file))

    def predict(self, seconds: float, latitude: float, longitude: float) -> dict[str, object]:
        predictions = predict_linear_softmax(self, [seconds, latitude, longitude])
        best = predictions[0]

        return {
            "country_code": COUNTRY_CODES[best["country_name"]],
            "country_name": best["country_name"],
            "confidence": round(best["probability"], 6),
            "probabilities": [
                {
                    "country_code": COUNTRY_CODES[entry["country_name"]],
                    "country_name": entry["country_name"],
                    "probability": round(entry["probability"], 6),
                }
                for entry in predictions
            ],
            "metadata": self.metadata,
        }


def standardize_features(features: list[float], scaler: dict[str, list[float]]) -> list[float]:
    return [
        (float(value) - scaler["mean"][index]) / (scaler["scale"][index] or 1.0)
        for index, value in enumerate(features)
    ]


def predict_linear_softmax(
    model: UfoLinearSoftmaxModel,
    raw_features: list[float],
) -> list[dict[str, float | str]]:
    features = standardize_features(raw_features, model.scaler)
    logits = []
    for class_index, weights in enumerate(model.coefficients):
        weighted = sum(weight * features[feature_index] for feature_index, weight in enumerate(weights))
        logits.append(weighted + model.intercepts[class_index])

    probabilities = softmax(logits)
    return sorted(
        [
            {"country_name": str(model.labels[index]), "probability": probability}
            for index, probability in enumerate(probabilities)
        ],
        key=lambda item: item["probability"],
        reverse=True,
    )


def softmax(logits: list[float]) -> list[float]:
    max_logit = max(logits)
    exps = [math.exp(logit - max_logit) for logit in logits]
    total = sum(exps)
    return [value / total for value in exps]

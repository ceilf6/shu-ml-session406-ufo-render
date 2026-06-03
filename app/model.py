from __future__ import annotations

import json
import math
from pathlib import Path


MODEL_PATH = Path(__file__).with_name("ufo-centroids.json")
COUNTRY_NAMES = {
    "au": "Australia",
    "ca": "Canada",
    "de": "Germany",
    "gb": "United Kingdom",
    "us": "United States",
}


class UfoCentroidModel:
    def __init__(self, payload: dict[str, object]) -> None:
        self.means = payload["feature_means"]
        self.scales = payload["feature_scales"]
        self.centroids = payload["centroids"]

    @classmethod
    def load(cls, path: Path = MODEL_PATH) -> "UfoCentroidModel":
        with path.open("r", encoding="utf-8") as model_file:
            return cls(json.load(model_file))

    def predict(self, seconds: float, latitude: float, longitude: float) -> dict[str, object]:
        features = self.scale_features([seconds, latitude, longitude])
        distances = {
            country: euclidean_distance(features, centroid)
            for country, centroid in self.centroids.items()
        }
        country_code = min(distances, key=distances.get)
        probabilities = distance_probabilities(distances)

        return {
            "country_code": country_code,
            "country_name": COUNTRY_NAMES[country_code],
            "confidence": round(probabilities[country_code], 6),
            "probabilities": [
                {
                    "country_code": code,
                    "country_name": COUNTRY_NAMES[code],
                    "probability": round(probabilities[code], 6),
                }
                for code in sorted(self.centroids)
            ],
        }

    def scale_features(self, values: list[float]) -> list[float]:
        return [
            (float(value) - float(mean)) / float(scale or 1.0)
            for value, mean, scale in zip(values, self.means, self.scales)
        ]


def euclidean_distance(left: list[float], right: list[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def distance_probabilities(distances: dict[str, float]) -> dict[str, float]:
    scores = {country: 1.0 / (distance + 1e-9) for country, distance in distances.items()}
    total = sum(scores.values())
    return {country: score / total for country, score in scores.items()}

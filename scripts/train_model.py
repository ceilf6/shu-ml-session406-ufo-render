from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


COUNTRIES = {"au", "ca", "de", "gb", "us"}


def train_centroids(csv_path: Path) -> dict[str, object]:
    rows: list[tuple[str, list[float]]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            country = (row["country"] or "").strip().lower()
            if country not in COUNTRIES:
                continue
            seconds = parse_float(row["duration (seconds)"])
            latitude = parse_float(row["latitude"])
            longitude = parse_float(row["longitude"])
            if seconds is None or latitude is None or longitude is None:
                continue
            if not 1 <= seconds <= 60:
                continue
            rows.append((country, [seconds, latitude, longitude]))

    means = column_means([features for _, features in rows])
    scales = column_scales([features for _, features in rows], means)

    grouped = {country: [] for country in sorted(COUNTRIES)}
    for country, features in rows:
        grouped[country].append(scale_features(features, means, scales))

    centroids = {
        country: [round(value, 6) for value in column_means(features)]
        for country, features in grouped.items()
    }

    return {
        "model": "nearest_country_centroid",
        "features": ["seconds", "latitude", "longitude"],
        "feature_means": [round(value, 6) for value in means],
        "feature_scales": [round(value, 6) for value in scales],
        "centroids": centroids,
        "training_rows": len(rows),
    }


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def column_means(rows: list[list[float]]) -> list[float]:
    width = len(rows[0])
    return [sum(row[index] for row in rows) / len(rows) for index in range(width)]


def column_scales(rows: list[list[float]], means: list[float]) -> list[float]:
    scales = []
    for index, mean in enumerate(means):
        variance = sum((row[index] - mean) ** 2 for row in rows) / len(rows)
        scales.append(math.sqrt(variance) or 1.0)
    return scales


def scale_features(values: list[float], means: list[float], scales: list[float]) -> list[float]:
    return [(value - mean) / scale for value, mean, scale in zip(values, means, scales)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("app/ufo-centroids.json"))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(train_centroids(args.csv_path), separators=(",", ":")),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_reports_ready():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "ready"}


def test_predict_returns_country_for_sighting_features():
    response = client.post(
        "/api/predict",
        json={"seconds": 20, "latitude": 53.2, "longitude": -2.916667},
    )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"country_code", "country_name", "confidence", "probabilities"}
    assert payload["country_code"] in {"au", "ca", "de", "gb", "us"}
    assert payload["country_name"] in {
        "Australia",
        "Canada",
        "Germany",
        "United Kingdom",
        "United States",
    }
    assert 0.0 <= payload["confidence"] <= 1.0

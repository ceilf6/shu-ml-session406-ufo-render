# Session 406 UFO Render App

This repository completes `session-406-3`: a real FastAPI backend for UFO sighting country prediction, deployed as one standalone Render web service.

## Stack

- FastAPI backend
- Uvicorn server
- Form frontend served by the backend
- JSON model artifact migrated from the optimized session app: standardized linear softmax classifier with 0.9447 test accuracy

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>, enter sighting features, and submit them to `/api/predict`.

## API

- `GET /health`
- `POST /api/predict`

```json
{
  "seconds": 20,
  "latitude": 53.2,
  "longitude": -2.916667
}
```

The model predicts one of Australia, Canada, Germany, United Kingdom, or United States.

## Render

Render uses `render.yaml`:

- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

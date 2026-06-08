# Session 406 UFO Render App

This repository completes the Session 406 UFO web app deployment tasks:

- `session-406-3`: deploy the UFO app as a standalone Render web service.
- `session-406-5`: containerize and deploy the UFO app using Docker.

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

## Run with Docker

Build the image:

```bash
docker build -t shu-ml-ufo .
```

If Docker Hub is slow from the local network, use a compatible Python mirror for
local verification:

```bash
docker build \
  --build-arg PYTHON_IMAGE=docker.m.daocloud.io/library/python:3.11-slim \
  --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
  -t shu-ml-ufo .
```

Run the container:

```bash
docker run --rm -p 8000:8000 -e PORT=8000 shu-ml-ufo
```

Verify the service:

```bash
curl http://127.0.0.1:8000/health
```

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

Render uses `render.yaml` with Docker runtime:

- Build: root `Dockerfile`
- Start: Dockerfile `CMD`, using Render's `$PORT`
- Health check: `/health`

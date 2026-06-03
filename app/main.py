from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.model import UfoCentroidModel


class PredictRequest(BaseModel):
    seconds: float = Field(..., ge=1, le=60)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


app = FastAPI(title="Session 406 UFO Predictor", version="1.0.0")
model = UfoCentroidModel.load()

static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": "ready"}


@app.post("/api/predict")
def predict(request: PredictRequest) -> dict[str, object]:
    return model.predict(request.seconds, request.latitude, request.longitude)

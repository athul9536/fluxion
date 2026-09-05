from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import ivr

app = FastAPI(title="Vani - Agricultural Helpline", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ivr.router)


@app.get("/")
def root():
    return {"service": "Vani Agricultural Helpline", "status": "running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "twilio": settings.twilio_enabled,
        "weather": settings.weather_enabled,
        "location": settings.default_location_name,
    }

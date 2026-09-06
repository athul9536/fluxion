"""GET /api/weather - current field weather via OpenWeatherMap."""

from fastapi import APIRouter

from app.schemas.weather import WeatherResponse
from app.services.weather_service import weather_service

router = APIRouter()


@router.get("/weather", response_model=WeatherResponse)
async def current_weather(lat: float | None = None, lon: float | None = None):
    return await weather_service.current(lat, lon)

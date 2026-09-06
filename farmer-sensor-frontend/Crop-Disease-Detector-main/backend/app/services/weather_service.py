"""OpenWeatherMap access. React never talks to OpenWeatherMap directly."""

from __future__ import annotations

import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

API_URL = "https://api.openweathermap.org/data/2.5/weather"
CACHE_TTL_SECONDS = 300
RAIN_WORDS = ("rain", "drizzle", "thunderstorm", "shower")


class WeatherService:
    def __init__(self) -> None:
        self._cache: dict[tuple[float, float], tuple[float, dict]] = {}

    @staticmethod
    def _demo(lat: float, lon: float, name: str, reason: str) -> dict:
        return {
            "temperature": 28.0,
            "humidity": 75,
            "condition": "Clouds",
            "description": "Partly cloudy",
            "icon": "04d",
            "wind_speed": 3.1,
            "rain_expected": False,
            "location": name,
            "latitude": lat,
            "longitude": lon,
            "source": reason,
        }

    async def current(
        self, latitude: float | None = None, longitude: float | None = None
    ) -> dict:
        lat = latitude if latitude is not None else settings.default_latitude
        lon = longitude if longitude is not None else settings.default_longitude
        fallback_name = (
            settings.default_location_name
            if latitude is None and longitude is None
            else f"{lat:.2f}, {lon:.2f}"
        )

        key = (round(lat, 2), round(lon, 2))
        cached = self._cache.get(key)
        if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
            return cached[1]

        if not settings.openweather_api_key.strip():
            return self._demo(lat, lon, fallback_name, "demo")

        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": settings.openweather_api_key.strip(),
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(API_URL, params=params)
                resp.raise_for_status()
                payload = resp.json()
        except Exception as exc:
            logger.warning("Weather lookup failed: %s", exc)
            return self._demo(lat, lon, fallback_name, "unavailable")

        weather = (payload.get("weather") or [{}])[0]
        condition = weather.get("main", "Unknown")
        description = (weather.get("description") or condition).title()
        data = {
            "temperature": round(float(payload.get("main", {}).get("temp", 0)), 1),
            "humidity": int(payload.get("main", {}).get("humidity", 0)),
            "condition": condition,
            "description": description,
            "icon": weather.get("icon"),
            "wind_speed": float(payload.get("wind", {}).get("speed", 0)),
            "rain_expected": any(w in condition.lower() for w in RAIN_WORDS)
            or "rain" in payload,
            "location": payload.get("name") or fallback_name,
            "latitude": lat,
            "longitude": lon,
            "source": "openweathermap",
        }
        if payload.get("sys", {}).get("country") and payload.get("name"):
            data["location"] = f"{payload['name']}, {payload['sys']['country']}"
        self._cache[key] = (time.time(), data)
        return data

    @staticmethod
    def as_context(data: dict) -> str:
        rain = "rain expected" if data.get("rain_expected") else "no rain expected now"
        return (
            f"{data['temperature']}C, {data['humidity']}% humidity, "
            f"{data['description']}, {rain}, at {data['location']}."
        )


weather_service = WeatherService()

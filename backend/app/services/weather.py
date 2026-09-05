"""OpenWeatherMap lookup. Returns stub data when no API key."""
import requests

from ..config import settings


def get_weather(lat: float, lng: float) -> dict:
    if not settings.weather_enabled:
        return {"summary": "clear", "temp_c": 28, "humidity": 70, "stub": True}
    
    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lng,
                "appid": settings.openweather_api_key,
                "units": "metric"
            },
            timeout=8,
        )
        resp.raise_for_status()
        d = resp.json()
        return {
            "summary": d["weather"][0]["description"],
            "temp_c": d["main"]["temp"],
            "humidity": d["main"]["humidity"],
            "stub": False,
        }
    except Exception:
        return {"summary": "unavailable", "temp_c": None, "humidity": None, "stub": True}

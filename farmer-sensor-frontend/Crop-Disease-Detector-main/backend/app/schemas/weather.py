from pydantic import BaseModel


class WeatherResponse(BaseModel):
    temperature: float
    humidity: int
    condition: str
    description: str
    icon: str | None = None
    wind_speed: float | None = None
    rain_expected: bool = False
    location: str
    latitude: float
    longitude: float
    source: str = "openweathermap"

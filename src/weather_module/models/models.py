from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Location(BaseModel):
    """Location data model. Used for querying the weather data."""
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    ip_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_query(self) -> str:
        """Convert the location to a query string."""
        if self.latitude and self.longitude:
            return f"{self.latitude},{self.longitude}"
        if self.zip_code:
            return self.zip_code
        if self.ip_address:
            return self.ip_address
        if self.city and self.country:
            return f"{self.city},{self.country}"
        if self.city and self.state:
            return f"{self.city},{self.state}"
        if self.city:
            return self.city
        if self.state:
            return self.state
        if self.country:
            return self.country
        raise ValueError("Location must have at least one valid attribute.")


class WeatherData(BaseModel):
    """Weather data model."""
    country: str
    state: Optional[str] = None
    city: str
    time_zone: Optional[str] = None
    temp_c: Optional[float] = None
    temp_f: Optional[float] = None
    temp_k: Optional[float] = None
    clouds: int
    wind_speed_kph: float
    wind_degree: Optional[int] = None
    wind_dir: Optional[str] = None
    pressure_mb: Optional[float] = None
    pressure_in: Optional[float] = None
    precip_mm: Optional[float] = None
    precip_in: Optional[float] = None
    humidity: Optional[int] = None
    feelslike_c: Optional[float] = None
    feelslike_f: Optional[float] = None
    vis_km: Optional[float] = None
    vis_miles: Optional[float] = None
    uv: Optional[float] = None
    gust_kph: Optional[float] = None
    gust_mph: Optional[float] = None
    last_updated: Optional[str] = None
    

class WeatherResponse(BaseModel):
    """Weather response model."""
    data: WeatherData
    message: str
    status: int

class WeatherRequest(BaseModel):
    """Weather request model."""
    query: str

class BulkWeatherRequest(BaseModel):
    locations: list[Location]

class BulkWeatherResponse(BaseModel):
    data: list[WeatherData]
    message: Optional[str] = None
    status: int = 200

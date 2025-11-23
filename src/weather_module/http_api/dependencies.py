"""FastAPI dependencies."""

from fastapi import Depends

from weather_module.config import get_settings
from weather_module.api.weather_client import WeatherClient
from weather_module.services.weather_service import WeatherService
from weather_module.cache.memory_cache import MemoryCache


def get_weather_client(settings = Depends(get_settings)) -> WeatherClient:
    return WeatherClient(
        api_key=settings.weather_api_key,
        base_url=settings.weather_api_base_url,
    )


def get_cache(settings = Depends(get_settings)) -> MemoryCache | None:
    """Get cache instance based on settings."""
    if not settings.cache_enabled:
        return None
    return MemoryCache()


def get_weather_service(
    client: WeatherClient = Depends(get_weather_client),
    cache: MemoryCache | None = Depends(get_cache),
    settings = Depends(get_settings),
) -> WeatherService:
    """Get WeatherService instance with dependencies injected."""
    return WeatherService(
        weather_client=client,
        cache=cache,
        cache_ttl=settings.cache_ttl_seconds,
        default_units="C",
    )

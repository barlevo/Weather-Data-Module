"""Configuration management for the weather module."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Weather API Configuration
    weather_api_key: str
    weather_api_base_url: str = "https://api.weatherapi.com/v1"
    
    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    
    # Server Configuration (optional)
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_to_console: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Use this function to get settings throughout your application.
    
    Example:
        settings = get_settings()
        api_key = settings.weather_api_key
    """
    return Settings()

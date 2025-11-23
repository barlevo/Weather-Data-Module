"""FastAPI HTTP layer package."""

from fastapi import FastAPI
from .routes import router as weather_router
from weather_module.config import get_settings
from weather_module.logging_config import setup_logging, get_logger

settings = get_settings()
setup_logging(
    level=settings.log_level, 
    log_file=settings.log_file,
    log_to_console=settings.log_to_console
)
logger = get_logger("http_api")

app = FastAPI(
    title="Weather Module API",
    description="HTTP API for querying weather data using the WeatherService.",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event():
    """Initialize logging on application startup."""
    logger.info("Weather Module API server starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown event."""
    logger.info("Weather Module API server shutting down")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "ok"}


app.include_router(weather_router)

__all__ = ["app"]
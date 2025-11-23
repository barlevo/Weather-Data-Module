"""FastAPI route definitions."""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List, Literal, Dict, Any

from weather_module.models.models import Location, WeatherData, BulkWeatherRequest
from weather_module.services.weather_service import WeatherService
from weather_module.logging_config import get_logger
from .dependencies import get_weather_service

logger = get_logger("http_api.routes")

router = APIRouter(
    prefix="/weather",
    tags=["weather"],
)


def _filter_weather_data(data: WeatherData, detailed: bool) -> Dict[str, Any]:
    """Filter WeatherData to include only basic or all fields based on detailed flag."""
    data_dict = data.model_dump()
    
    if not detailed:
        basic_fields = {
            "country", "state", "city", "time_zone",
            "temp_c", "temp_f", "temp_k",
            "clouds", "wind_speed_kph"
        }
        return {k: v for k, v in data_dict.items() if k in basic_fields}
    
    return data_dict


@router.get(
    "/current",
    summary="Get current weather for a single location",
)
def get_current_weather(
    city: Optional[str] = Query(None, description="City name, e.g. 'Berlin'"),
    country: Optional[str] = Query(None, description="Country name, e.g. 'Germany'"),
    state: Optional[str] = Query(None, description="State/region name"),
    zip_code: Optional[str] = Query(None, description="Zip code, e.g. '10001'"),
    units: Optional[str] = Query("C", description="Temperature units: C, F, K, BOTH, ALL"),
    detailed: bool = Query(False, description="Include detailed weather data (pressure, humidity, UV, etc.)"),
    service: WeatherService = Depends(get_weather_service),
) -> Dict[str, Any]:
    """Return current weather using the core WeatherService.
    
    By default, returns basic weather data. Set detailed=true to include
    additional fields like pressure, humidity, UV index, wind direction, etc.
    """
    logger.info(f"GET /weather/current - city={city}, country={country}, state={state}, "
                f"zip_code={zip_code}, units={units}, detailed={detailed}")
    
    location = Location(city=city, country=country, state=state, zip_code=zip_code)
    try:
        query = location.to_query()
        logger.debug(f"Location query: {query}")
    except ValueError as e:
        logger.warning(f"Invalid location parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        weather_data = service.get_current_weather(location, units)
        filtered_data = _filter_weather_data(weather_data, detailed)
        logger.info(f"Successfully retrieved weather data for {weather_data.city}")
        
        return {
            "data": filtered_data,
            "message": "ok",
            "status": 200
        }
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@router.post(
    "/bulk",
    summary="Get current weather for multiple locations in a single request",
)
def get_current_weather_bulk(
    request: BulkWeatherRequest,
    units: Optional[str] = Query("C", description="Temperature units: C, F, K, BOTH, ALL"),
    detailed: bool = Query(False, description="Include detailed weather data (pressure, humidity, UV, etc.)"),
    service: WeatherService = Depends(get_weather_service),
) -> Dict[str, Any]:
    """Bulk weather endpoint.

    - Accepts a list of Location objects in the request body.
    - Uses WeatherAPI's bulk endpoint under the hood via WeatherService.
    - Returns a list of WeatherData in the same order as the input locations.
    - Set detailed=true to include additional fields.
    """
    logger.info(f"POST /weather/bulk - locations={len(request.locations)}, "
                f"units={units}, detailed={detailed}")
    
    if not request.locations:
        logger.warning("Bulk request received with empty locations list")
        raise HTTPException(status_code=400, detail="At least one location is required.")

    for i, loc in enumerate(request.locations, start=1):
        try:
            query = loc.to_query()
            logger.debug(f"Location {i}: {query}")
        except ValueError as e:
            logger.warning(f"Invalid location at index {i}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid location at index {i}: {e}",
            )

    try:
        weather_data = service.get_current_weather_bulk(request.locations, units=units)
        filtered_data = [_filter_weather_data(wd, detailed) for wd in weather_data]
        logger.info(f"Successfully retrieved weather data for {len(filtered_data)} locations")
        
        return {
            "data": filtered_data,
            "message": "ok",
            "status": 200
        }
    except Exception as e:
        logger.error(f"Error fetching bulk weather data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")
"""Weather service business logic."""
from weather_module.api.weather_client import WeatherClient
from weather_module.models.models import WeatherData, Location
from weather_module.cache.memory_cache import MemoryCache
from typing import Optional, List
from weather_module.logging_config import get_logger

logger = get_logger("services.weather_service")



class WeatherService:
    """Weather service business logic.
    This service is responsible for the business logic of the weather module.
    It is responsible for getting the weather data for a city.
    """
    def __init__(self, weather_client: WeatherClient,cache=None, cache_ttl: int = 900, default_units: str = "C"):
        self.weather_client = weather_client
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.default_units = default_units.upper()
  
    def get_current_weather(self, location: Location, units: Optional[str] = None) -> WeatherData:
        """Get current weather data for a city."""
        units = (units or self.default_units).upper()
        query = location.to_query()
        cache_key = f"{query}|units={units}"
        
        if self.cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for query: {query} (units={units})")
                return cached_data
            logger.debug(f"Cache miss for query: {query} (units={units})")
        
        logger.debug(f"Fetching weather data from API for: {query} (units={units})")
        data = self.weather_client.get_current_weather(query)
        processed_data = self._apply_units(data, units)
        
        if self.cache:
            logger.debug(f"Caching weather data for: {query} (units={units}, TTL={self.cache_ttl}s)")
            self.cache.set(cache_key, processed_data, self.cache_ttl)
        return processed_data
    
    
    def get_current_weather_bulk(
        self,
        locations: List[Location],
        units: Optional[str] = None,
    ) -> List[WeatherData]:
        """
        Get current weather for multiple locations using WeatherAPI bulk endpoint.
        """
        if not locations:
            logger.debug("Empty locations list provided to bulk method")
            return []

        effective_units = (units or self.default_units).upper()
        logger.info(f"Fetching bulk weather for {len(locations)} locations (units={effective_units})")

        raw_results = self.weather_client.get_current_weather_bulk(locations)

        processed: List[WeatherData] = []
        for wd in raw_results:
            if wd:
                processed.append(self._apply_units(wd, effective_units))

        logger.info(f"Successfully processed {len(processed)} weather results")
        return processed


    def _apply_units(self, wd: WeatherData, units: str) -> WeatherData:
        """Return a WeatherData object consistent with configured units."""
        def c_to_k(c: float) -> float:
            return c + 273.15

        def f_to_k(f: float) -> float:
            return (f - 32.0) * 5.0 / 9.0 + 273.15

        base_c = wd.temp_c
        base_f = wd.temp_f

        base_k: Optional[float] = None
        if units in ("K", "ALL") and (base_c is not None or base_f is not None):
            if base_c is not None:
                base_k = c_to_k(base_c)
            elif base_f is not None:
                base_k = f_to_k(base_f)

        common_fields = {
            "country": wd.country,
            "state": wd.state,
            "city": wd.city,
            "time_zone": wd.time_zone,
            "clouds": wd.clouds,
            "wind_speed_kph": wd.wind_speed_kph,
            "wind_degree": wd.wind_degree,
            "wind_dir": wd.wind_dir,
            "pressure_mb": wd.pressure_mb,
            "pressure_in": wd.pressure_in,
            "precip_mm": wd.precip_mm,
            "precip_in": wd.precip_in,
            "humidity": wd.humidity,
            "feelslike_c": wd.feelslike_c,
            "feelslike_f": wd.feelslike_f,
            "vis_km": wd.vis_km,
            "vis_miles": wd.vis_miles,
            "uv": wd.uv,
            "gust_kph": wd.gust_kph,
            "gust_mph": wd.gust_mph,
            "last_updated": wd.last_updated,
        }

        if units == "C":
            return WeatherData(
                temp_c=base_c,
                temp_f=None,
                temp_k=None,
                **common_fields,
            )

        if units == "F":
            return WeatherData(
                temp_c=None,
                temp_f=base_f,
                temp_k=None,
                **common_fields,
            )

        if units == "K":
            return WeatherData(
                temp_c=None,
                temp_f=None,
                temp_k=base_k,
                **common_fields,
            )

        if units == "BOTH":  # C + F
            return WeatherData(
                temp_c=base_c,
                temp_f=base_f,
                temp_k=None,
                **common_fields,
            )

        if units == "ALL":  # C + F + K
            return WeatherData(
                temp_c=base_c,
                temp_f=base_f,
                temp_k=base_k,
                **common_fields,
            )

        return wd

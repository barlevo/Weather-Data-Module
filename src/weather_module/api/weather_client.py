"""WeatherAPI client for external weather data."""

import requests
from weather_module.models.models import WeatherData
from typing import List
from weather_module.models.models import Location
from weather_module.logging_config import get_logger

logger = get_logger("api.weather_client")

class WeatherClientError(Exception):
    """Raised when the WeatherAPI client encounters an error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class WeatherClient:
    """WeatherAPI client for external weather data."""

    def __init__(self, api_key: str, base_url: str = "https://api.weatherapi.com/v1", timeout: int = 10):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    def get_current_weather_bulk(self, locations: List[Location]) -> List[WeatherData]:
        """Get current weather data for a list of locations.
        Args:
            locations: List of Location objects.
        Returns:
            List of WeatherData objects.
        Raises:
            WeatherClientError: If the request fails.
        """
        if not locations:
            logger.debug("Empty locations list provided, returning empty list")
            return []

        logger.info(f"Fetching bulk weather data for {len(locations)} locations")
        
        url = f"{self.base_url}/current.json"
        params = {
            "key": self.api_key,
            "q": "bulk",
        }

        bulk_locations = []
        id_to_index: dict[str, int] = {}

        for idx, loc in enumerate(locations):
            q = loc.to_query()
            custom_id = str(idx)
            id_to_index[custom_id] = idx

            bulk_locations.append({
                "q": q,
                "custom_id": custom_id,
            })
            logger.debug(f"Added location {idx}: {q}")

        body = {"locations": bulk_locations}

        logger.debug(f"Sending bulk request to {url}")
        try:
            response = requests.post(
                url,
                params=params,
                json=body,
                timeout=self.timeout,
            )
            logger.debug(f"Received response with status code {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Network error during bulk weather request: {e}")
            raise WeatherClientError(f"Network error: {e}") from e

        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"Bulk weather request failed: {response.status_code} - {error_msg}")
            raise WeatherClientError(
                f"Failed bulk weather request: {response.status_code} {error_msg}"
            )

        raw = response.json()
        bulk_items = raw.get("bulk", [])
        logger.debug(f"Processing {len(bulk_items)} bulk items from API response")

        results: List[WeatherData] = [None] * len(locations) 

        for item in bulk_items:
            query_block = item.get("query", {})
            custom_id = query_block.get("custom_id")
            location_block = query_block.get("location", {})
            current_block = query_block.get("current", {})

            if custom_id is None or custom_id not in id_to_index:
                logger.warning(f"Skipping item with invalid custom_id: {custom_id}")
                continue

            idx = id_to_index[custom_id]

            def get_numeric(key, default=None):
                value = current_block.get(key)
                return value if value is not None and value != "" else default

            results[idx] = WeatherData(
                country=location_block["country"],
                state=location_block.get("region") or None,
                city=location_block["name"],
                time_zone=location_block.get("tz_id") or None,
                temp_c=current_block.get("temp_c"),
                temp_f=current_block.get("temp_f"),
                temp_k=None,
                clouds=current_block.get("cloud", 0),
                wind_speed_kph=current_block.get("wind_kph", 0.0),
                wind_degree=get_numeric("wind_degree"),
                wind_dir=current_block.get("wind_dir"),
                pressure_mb=get_numeric("pressure_mb"),
                pressure_in=get_numeric("pressure_in"),
                precip_mm=get_numeric("precip_mm"),
                precip_in=get_numeric("precip_in"),
                humidity=get_numeric("humidity"),
                feelslike_c=get_numeric("feelslike_c"),
                feelslike_f=get_numeric("feelslike_f"),
                vis_km=get_numeric("vis_km"),
                vis_miles=get_numeric("vis_miles"),
                uv=get_numeric("uv"),
                gust_kph=get_numeric("gust_kph"),
                gust_mph=get_numeric("gust_mph"),
                last_updated=current_block.get("last_updated"),
            )
            logger.debug(f"Processed weather data for location {idx}: {location_block.get('name')}")

        logger.info(f"Successfully fetched bulk weather data for {len([r for r in results if r is not None])} locations")
        return results


    def get_current_weather(self, query: str) -> WeatherData:
        """Get current weather data for a city. 
        Args:
            query:
            - The city name (e.g. "London"),
            - state (e.g. "England"),
            - country (e.g. "United Kingdom"),
            - zip code (e.g. "EC2Y 5AA"),   
            - or latitude and longitude (e.g. "40.7128,-74.0060")
            to get weather data for. Must be a valid query.
        Returns:
            WeatherData: The weather data for the city.
        Raises:
            WeatherClientError: If the request fails.
        """
        logger.info(f"Fetching current weather for query: {query}")
        
        url = f"{self.base_url}/current.json"
        params = {
            "key": self.api_key,
            "q": query,
        }
        
        logger.debug(f"Sending request to {url} with query={query}")
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            logger.debug(f"Received response with status code {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Network error during weather request for '{query}': {e}")
            raise WeatherClientError(f"Network error: {e}") from e
        
        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"WeatherAPI request failed for '{query}': {response.status_code} - {error_msg}")
            raise WeatherClientError(f"WeatherAPI request failed: {response.status_code} {error_msg}")
        
        raw = response.json()
        location_block = raw["location"]
        current_block = raw["current"]
        logger.debug(f"Successfully retrieved weather data for {location_block.get('name', query)}")
        
        def get_numeric(key, default=None):
            value = current_block.get(key)
            return value if value is not None and value != "" else default
        
        return WeatherData(
            country=location_block["country"],
            state=location_block.get("region") or None,
            city=location_block["name"],
            time_zone=location_block.get("tz_id") or None,
            temp_c=current_block.get("temp_c"),
            temp_f=current_block.get("temp_f"),
            temp_k=None,
            clouds=current_block.get("cloud", 0),
            wind_speed_kph=current_block.get("wind_kph", 0.0),
            wind_degree=get_numeric("wind_degree"),
            wind_dir=current_block.get("wind_dir"),
            pressure_mb=get_numeric("pressure_mb"),
            pressure_in=get_numeric("pressure_in"),
            precip_mm=get_numeric("precip_mm"),
            precip_in=get_numeric("precip_in"),
            humidity=get_numeric("humidity"),
            feelslike_c=get_numeric("feelslike_c"),
            feelslike_f=get_numeric("feelslike_f"),
            vis_km=get_numeric("vis_km"),
            vis_miles=get_numeric("vis_miles"),
            uv=get_numeric("uv"),
            gust_kph=get_numeric("gust_kph"),
            gust_mph=get_numeric("gust_mph"),
            last_updated=current_block.get("last_updated"),
        )
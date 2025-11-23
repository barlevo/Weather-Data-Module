
from typing import Optional

from weather_module.config import get_settings
from weather_module.api.weather_client import WeatherClient
from weather_module.services.weather_service import WeatherService
from weather_module.io.csv_reader import CSVReader
from weather_module.io.csv_writer import CSVWriter
from weather_module.cache.memory_cache import MemoryCache
from weather_module.logging_config import get_logger

logger = get_logger("pipeline") 


def run_pipeline(
    input_csv: str,
    output_csv: str,
    units: str = "C",
    use_cache: bool = True,
    cache_ttl: int = 900,
    max_rows: Optional[int] = None,
    verbose: bool = False,
    use_bulk: bool = False,
    detailed: bool = False,
) -> None:
    """
    End-to-end pipeline:
    - read locations from input CSV
    - fetch weather for each location (with optional cache)
    - write enriched results to output CSV
    """
    logger.info(f"Starting pipeline: input={input_csv}, output={output_csv}, units={units}, "
                f"cache={'enabled' if use_cache else 'disabled'}, bulk={use_bulk}, detailed={detailed}")
    
    settings = get_settings()
    client = WeatherClient(
        api_key=settings.weather_api_key,
        base_url=settings.weather_api_base_url,
    )
    cache = MemoryCache() if use_cache else None
    service = WeatherService(weather_client=client, cache=cache, cache_ttl=cache_ttl, default_units=units)
    logger.debug("Initialized WeatherClient and WeatherService")

    logger.info(f"Reading locations from {input_csv}")
    reader = CSVReader(input_csv)
    locations = reader.read()
    
    if max_rows is not None:
        original_count = len(locations)
        locations = locations[:max_rows]
        logger.info(f"Limited locations from {original_count} to {len(locations)} rows")
    
    logger.info(f"Read {len(locations)} locations from {input_csv}")
    
    if use_bulk:
        logger.info("Using bulk API endpoint for fetching weather data")
        weather_list = service.get_current_weather_bulk(locations, units)
    else:
        logger.info("Using per-location API endpoint for fetching weather data")
        weather_list = []
        for i, loc in enumerate(locations, 1):
            logger.debug(f"Fetching weather for location {i}/{len(locations)}: {loc.to_query()}")
            weather_list.append(service.get_current_weather(loc, units))
    
    results = list(zip(locations, weather_list))
    logger.info(f"Successfully fetched weather data for {len(results)} locations")
    
    logger.info(f"Writing results to {output_csv} (units={units}, detailed={detailed})")
    writer = CSVWriter(output_csv, units=units, detailed=detailed)
    writer.write(results)
    logger.info(f"Pipeline completed successfully. Wrote {len(results)} rows to {output_csv}")
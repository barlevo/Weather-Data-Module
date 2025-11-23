"""Tests for Weather Service."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weather_module.models.models import Location, WeatherData
from src.weather_module.services.weather_service import WeatherService
from src.weather_module.api.weather_client import WeatherClient, WeatherClientError
from src.weather_module.cache.memory_cache import MemoryCache


# Sample weather data for tests
MOCK_WEATHER_DATA = WeatherData(
    country="United Kingdom",
    state="City of London, Greater London",
    city="London",
    time_zone="Europe/London",
    temp_c=15.5,
    temp_f=59.9,
    clouds=75,
    wind_speed_kph=12.5
)


class TestWeatherService:
    """Essential tests for Weather Service."""

    def test_get_current_weather_from_api_when_cache_miss(self):
        """Test getting weather data from API when cache is empty."""
        # Arrange
        mock_client = Mock(spec=WeatherClient)
        mock_client.get_current_weather.return_value = MOCK_WEATHER_DATA
        
        cache = MemoryCache()
        service = WeatherService(weather_client=mock_client, cache=cache)
        location = Location(city="London")
        
        # Act
        result = service.get_current_weather(location)
        
        # Assert
        assert isinstance(result, WeatherData)
        assert result.city == "London"
        assert result.country == "United Kingdom"
        mock_client.get_current_weather.assert_called_once_with("London")

    def test_get_current_weather_from_cache_when_cache_hit(self):
        """Test getting weather data from cache when available (within TTL)."""
        # Arrange
        mock_client = Mock(spec=WeatherClient)
        mock_client.get_current_weather.return_value = MOCK_WEATHER_DATA
        
        cache = MemoryCache()
        service = WeatherService(weather_client=mock_client, cache=cache, cache_ttl=900)
        location = Location(city="London")
        
        # First call - populates cache
        service.get_current_weather(location)
        mock_client.reset_mock()
        
        # Act - Second call should use cache (within TTL)
        result = service.get_current_weather(location)
        
        # Assert - Client should not be called again (cache hit)
        assert isinstance(result, WeatherData)
        assert result.city == "London"
        assert result.country == "United Kingdom"
        mock_client.get_current_weather.assert_not_called()

    def test_cache_is_set_after_api_call_with_ttl(self):
        """Test that weather data is cached after API call with TTL."""
        # Arrange
        mock_client = Mock(spec=WeatherClient)
        mock_client.get_current_weather.return_value = MOCK_WEATHER_DATA
        
        cache = MemoryCache()
        service = WeatherService(weather_client=mock_client, cache=cache, cache_ttl=900)
        location = Location(city="London")
        query = location.to_query()
        
        # Verify cache is empty
        assert cache.get(query) is None
        
        # Act - First call should cache the data with TTL
        service.get_current_weather(location)
        
        # Assert - Cache should now contain the data (not expired)
        cached_data = cache.get(query)
        assert cached_data is not None
        assert cached_data.city == "London"
        assert cached_data.temp_c == 15.5
        
        # Verify cache entry has expiration set
        assert query in cache.cache
        assert "expires_at" in cache.cache[query]

    def test_get_current_weather_handles_client_error(self):
        """Test that service propagates errors from weather client."""
        # Arrange
        mock_client = Mock(spec=WeatherClient)
        mock_client.get_current_weather.side_effect = WeatherClientError("API Error")
        
        cache = MemoryCache()
        service = WeatherService(weather_client=mock_client, cache=cache)
        location = Location(city="InvalidCity")
        
        # Act & Assert
        with pytest.raises(WeatherClientError) as exc_info:
            service.get_current_weather(location)
        
        assert "API Error" in str(exc_info.value)

    def test_cache_expires_after_ttl(self):
        """Test that cached data expires after TTL and triggers new API call."""
        # Arrange
        mock_client = Mock(spec=WeatherClient)
        mock_client.get_current_weather.return_value = MOCK_WEATHER_DATA
        
        cache = MemoryCache()
        service = WeatherService(weather_client=mock_client, cache=cache, cache_ttl=60)  # 60 seconds TTL
        location = Location(city="London")
        
        # Mock time BEFORE setting cache, so both set() and get() use mocked time
        with patch('src.weather_module.cache.memory_cache.time.time') as mock_time:
            # Start at time 1000
            current_time = 1000.0
            mock_time.return_value = current_time
            
            # First call - populates cache (expires at 1000 + 60 = 1060)
            service.get_current_weather(location)
            mock_client.reset_mock()
            
            # Advance time to 1061 (past expiration)
            mock_time.return_value = 1061.0
            
            # Act - Should fetch from API again (cache expired)
            result = service.get_current_weather(location)
            
            # Assert - Client should be called again (cache expired)
            assert isinstance(result, WeatherData)
            assert result.city == "London"
            mock_client.get_current_weather.assert_called_once_with("London")

    def test_cache_uses_correct_ttl(self):
        """Test that service uses the configured TTL when setting cache."""
        # Arrange
        mock_client = Mock(spec=WeatherClient)
        mock_client.get_current_weather.return_value = MOCK_WEATHER_DATA
        
        cache = MemoryCache()
        custom_ttl = 900  # 15 minutes = 900 seconds
        service = WeatherService(weather_client=mock_client, cache=cache, cache_ttl=custom_ttl)
        location = Location(city="London")
        query = location.to_query()
        
        # Act - First call should cache with custom TTL
        service.get_current_weather(location)
        
        # Assert - Verify cache entry has correct expiration time
        assert query in cache.cache
        entry = cache.cache[query]
        assert "expires_at" in entry
        
        # Check that expiration is approximately custom_ttl seconds from now
        expected_expires_at = time.time() + custom_ttl
        actual_expires_at = entry["expires_at"]
        # Allow 1 second tolerance for test execution time
        assert abs(actual_expires_at - expected_expires_at) < 2

    def test_cache_works_without_cache_instance(self):
        """Test that service works correctly when no cache is provided."""
        # Arrange
        mock_client = Mock(spec=WeatherClient)
        mock_client.get_current_weather.return_value = MOCK_WEATHER_DATA
        
        # Service without cache
        service = WeatherService(weather_client=mock_client, cache=None)
        location = Location(city="London")
        
        # Act - Should work without cache
        result = service.get_current_weather(location)
        
        # Assert
        assert isinstance(result, WeatherData)
        assert result.city == "London"
        mock_client.get_current_weather.assert_called_once_with("London")
        
        # Second call should still hit API (no cache)
        mock_client.reset_mock()
        result2 = service.get_current_weather(location)
        mock_client.get_current_weather.assert_called_once_with("London")

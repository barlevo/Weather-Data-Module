"""Tests for Weather API client."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import requests

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weather_module.api.weather_client import WeatherClient, WeatherClientError
from src.weather_module.models.models import WeatherData
from src.weather_module.config import get_settings


# Sample mock response data
MOCK_WEATHER_RESPONSE = {
    "location": {
        "name": "London",
        "region": "City of London, Greater London",
        "country": "United Kingdom",
        "tz_id": "Europe/London",
    },
    "current": {
        "temp_c": 15.5,
        "temp_f": 59.9,
        "cloud": 75,
        "wind_kph": 12.5,
    }
}


class TestWeatherClient:
    """Essential tests for Weather API client."""

    def test_get_current_weather_success_mocked(self):
        """Test successful weather data retrieval with mocked response."""
        # Arrange
        client = WeatherClient(api_key="test_key")
        
        # Mock the requests.get call
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = MOCK_WEATHER_RESPONSE
            mock_response.text = ""
            mock_get.return_value = mock_response
            
            # Act
            result = client.get_current_weather("London")
            
            # Assert
            assert isinstance(result, WeatherData)
            assert result.city == "London"
            assert result.country == "United Kingdom"
            assert result.temp_c == 15.5
            assert result.wind_speed_kph == 12.5

    def test_get_current_weather_http_error(self):
        """Test error handling for HTTP errors."""
        # Arrange
        client = WeatherClient(api_key="test_key")
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_get.return_value = mock_response
            
            # Act & Assert
            with pytest.raises(WeatherClientError) as exc_info:
                client.get_current_weather("InvalidCity")
            
            assert "404" in str(exc_info.value)
            assert "Not Found" in str(exc_info.value)

    def test_get_current_weather_network_error(self):
        """Test error handling for network connection errors."""
        # Arrange
        client = WeatherClient(api_key="test_key")
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            # Act & Assert
            with pytest.raises(requests.exceptions.ConnectionError):
                client.get_current_weather("London")

    @pytest.mark.integration
    def test_get_current_weather_real_api(self):
        """Test with real API call (requires API key in .env)."""
        # Skip if no API key configured
        try:
            settings = get_settings()
            if not settings.weather_api_key or settings.weather_api_key == "your_api_key_here":
                pytest.skip("Weather API key not configured")
        except Exception:
            pytest.skip("Settings not configured")
        
        # Arrange
        settings = get_settings()
        client = WeatherClient(
            api_key=settings.weather_api_key,
            base_url=settings.weather_api_base_url
        )
        
        # Act
        result = client.get_current_weather("London")
        
        # Assert
        assert isinstance(result, WeatherData)
        assert result.city == "London"
        assert result.country == "United Kingdom"
        assert result.temp_c is not None
        assert result.wind_speed_kph is not None

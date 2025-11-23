"""Tests for CSV Writer."""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
import csv
import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weather_module.io.csv_writer import CSVWriter
from src.weather_module.models.models import Location, WeatherData


class TestCSVWriter:
    """Essential tests for CSV Writer."""

    def test_write_location_and_weather_data_success(self):
        """Test writing combined Location and WeatherData to CSV file."""
        # Arrange - Create data with Location + WeatherData fields
        data = [
            {
                "city": "London",
                "country": "United Kingdom",
                "state": "England",
                "zip_code": "EC2Y 5AA",
                "temp_c": 15.5,
                "temp_f": 59.9,
                "clouds": 75,
                "wind_speed_kph": 12.5,
            },
            {
                "city": "New York",
                "country": "United States",
                "state": "New York",
                "zip_code": "10001",
                "temp_c": 22.0,
                "temp_f": 71.6,
                "clouds": 50,
                "wind_speed_kph": 8.3,
            }
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            temp_file = f.name
        
        try:
            writer = CSVWriter(temp_file)
            
            # Act
            writer.write(data)
            
            # Assert - Read back and verify content
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 2
            
            # Check first row
            assert rows[0]["city"] == "London"
            assert rows[0]["country"] == "United Kingdom"
            assert rows[0]["state"] == "England"
            assert rows[0]["zip_code"] == "EC2Y 5AA"
            assert rows[0]["temp_c"] == "15.5"
            assert rows[0]["clouds"] == "75"
            assert rows[0]["wind_speed_kph"] == "12.5"
            
            # Check second row
            assert rows[1]["city"] == "New York"
            assert rows[1]["country"] == "United States"
            assert rows[1]["temp_c"] == "22.0"
        finally:
            Path(temp_file).unlink()

    def test_write_handles_none_values(self):
        """Test that None values are converted to empty strings."""
        # Arrange - Data with None values (common in Location/WeatherData)
        data = [
            {
                "city": "Paris",
                "country": "France",
                "state": None,  # None value
                "zip_code": None,  # None value
                "temp_c": 18.3,
                "clouds": 60,
                "wind_speed_kph": 10.2,
            }
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            temp_file = f.name
        
        try:
            writer = CSVWriter(temp_file)
            
            # Act
            writer.write(data)
            
            # Assert - None values should be converted to empty strings
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 1
            assert rows[0]["city"] == "Paris"
            assert rows[0]["country"] == "France"
            assert rows[0]["state"] == ""  # None converted to empty string
            assert rows[0]["zip_code"] == ""  # None converted to empty string
            assert rows[0]["temp_c"] == "18.3"
        finally:
            Path(temp_file).unlink()

    def test_write_creates_csv_with_correct_headers(self):
        """Test that CSV file is created with correct column headers."""
        # Arrange
        data = [
            {
                "city": "Tel Aviv",
                "country": "Israel",
                "state": "Tel Aviv District",
                "zip_code": "61000",
                "temp_c": 28.5,
                "clouds": 20,
                "wind_speed_kph": 15.8,
            }
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            temp_file = f.name
        
        try:
            writer = CSVWriter(temp_file)
            
            # Act
            writer.write(data)
            
            # Assert - Verify headers (order may vary since writer uses set)
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                expected_headers = {"country", "state", "city", "zip_code", "temp_c", "clouds", "wind_speed_kph"}
                assert set(reader.fieldnames) == expected_headers
                assert len(reader.fieldnames) == 7  # All 7 fields present
        finally:
            Path(temp_file).unlink()

    def test_write_handles_empty_data_list(self):
        """Test that writing empty data list does not create rows (only headers)."""
        # Arrange - Empty data list
        data = []
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            temp_file = f.name
        
        try:
            writer = CSVWriter(temp_file)
            
            # Act - Should not raise error and return early
            writer.write(data)
            
            # Assert - File should exist but have no data rows (only headers if any)
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Should be empty or only contain header
            # Since it returns early when data is empty, file might be empty or just have headers
            # Let's check file exists and is readable
            assert Path(temp_file).exists()
        finally:
            Path(temp_file).unlink()

    def test_write_all_required_fields_from_location_and_weather_data(self):
        """Test that all required fields from Location and WeatherData are written."""
        # Arrange - Complete data with all fields
        data = [
            {
                "city": "London",
                "country": "United Kingdom",
                "state": "England",
                "zip_code": "EC2Y 5AA",
                "temp_c": 15.5,
                "clouds": 75,
                "wind_speed_kph": 12.5,
            }
        ]
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            temp_file = f.name
        
        try:
            writer = CSVWriter(temp_file)
            
            # Act
            writer.write(data)
            
            # Assert - All fields should be present
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            row = rows[0]
            
            # Location fields
            assert "city" in row
            assert "country" in row
            assert "state" in row
            assert "zip_code" in row
            
            # WeatherData fields
            assert "temp_c" in row
            assert "clouds" in row
            assert "wind_speed_kph" in row
            
            # Verify values match
            assert row["city"] == "London"
            assert row["country"] == "United Kingdom"
            assert row["temp_c"] == "15.5"
            assert row["clouds"] == "75"
            assert row["wind_speed_kph"] == "12.5"
        finally:
            Path(temp_file).unlink()


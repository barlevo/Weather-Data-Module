"""Tests for CSV Reader."""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weather_module.io.csv_reader import CSVReader
from src.weather_module.models.models import Location


class TestCSVReader:
    """Essential tests for CSV Reader."""

    def test_read_valid_csv_with_all_fields(self):
        """Test reading a valid CSV file with all location fields."""
        # Arrange - Create temporary CSV file
        csv_content = """city,country,state,postal_code,ip_address,latitude,longitude
London,United Kingdom,England,EC2Y 5AA,,51.5074,-0.1278
New York,United States,New York,10001,,40.7128,-74.0060"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            reader = CSVReader(temp_file)
            
            # Act
            locations = reader.read()
            
            # Assert
            assert len(locations) == 2
            assert isinstance(locations[0], Location)
            assert isinstance(locations[1], Location)
            
            # Check first location
            assert locations[0].city == "London"
            assert locations[0].country == "United Kingdom"
            assert locations[0].state == "England"
            assert locations[0].postal_code == "EC2Y 5AA"
            assert locations[0].latitude == 51.5074
            assert locations[0].longitude == -0.1278
            
            # Check second location
            assert locations[1].city == "New York"
            assert locations[1].country == "United States"
            assert locations[1].state == "New York"
        finally:
            Path(temp_file).unlink()

    def test_read_csv_with_missing_fields(self):
        """Test reading CSV file with missing fields (should handle gracefully)."""
        # Arrange - Create CSV with only some fields
        csv_content = """city,country
London,United Kingdom
Paris,France"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            reader = CSVReader(temp_file)
            
            # Act
            locations = reader.read()
            
            # Assert
            assert len(locations) == 2
            assert locations[0].city == "London"
            assert locations[0].country == "United Kingdom"
            assert locations[0].state is None  # Missing field should be None
            assert locations[0].postal_code is None
            
            assert locations[1].city == "Paris"
            assert locations[1].country == "France"
        finally:
            Path(temp_file).unlink()

    def test_read_csv_cleans_whitespace_and_empty_strings(self):
        """Test that CSV reader cleans whitespace and converts empty strings to None."""
        # Arrange - Create CSV with whitespace and empty strings
        csv_content = """city,country,state,postal_code
  London  ,  United Kingdom  ,  ,  
New York,United States,  ,  """
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            reader = CSVReader(temp_file)
            
            # Act
            locations = reader.read()
            
            # Assert
            assert len(locations) == 2
            
            # First location - whitespace should be stripped
            assert locations[0].city == "London"  # Whitespace stripped
            assert locations[0].country == "United Kingdom"  # Whitespace stripped
            assert locations[0].state is None  # Empty string converted to None
            assert locations[0].postal_code is None  # Empty string converted to None
            
            # Second location
            assert locations[1].city == "New York"
            assert locations[1].country == "United States"
            assert locations[1].state is None
            assert locations[1].postal_code is None
        finally:
            Path(temp_file).unlink()

    def test_read_csv_skips_invalid_rows(self):
        """Test that CSV reader skips invalid rows and continues processing."""
        # Arrange - Create CSV with one invalid row (invalid latitude)
        csv_content = """city,country,latitude,longitude
London,United Kingdom,51.5074,-0.1278
InvalidCity,InvalidCountry,not_a_number,-0.1278
Paris,France,48.8566,2.3522"""
        
        with NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(csv_content)
            temp_file = f.name
        
        try:
            reader = CSVReader(temp_file)
            
            # Act
            locations = reader.read()
            
            # Assert - Should skip invalid row and return only valid locations
            assert len(locations) == 2  # Invalid row skipped
            
            # First valid location
            assert locations[0].city == "London"
            assert locations[0].country == "United Kingdom"
            assert locations[0].latitude == 51.5074
            
            # Second valid location (third row, second one was skipped)
            assert locations[1].city == "Paris"
            assert locations[1].country == "France"
            assert locations[1].latitude == 48.8566
        finally:
            Path(temp_file).unlink()


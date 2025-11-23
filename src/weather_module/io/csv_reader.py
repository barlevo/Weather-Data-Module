"""CSV file reading utilities."""

import csv
from weather_module.models.models import Location
from typing import Optional
from pydantic import ValidationError


class CSVReader:
    """CSV file reading utilities."""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _clean_row(self, row: dict[str, str]) -> dict[str, Optional[str]]:
        """Clean CSV row:
            - Strip whitespaces
            - Convert empty strings to None
            - keep only fields that exist in Location model
            """
        cleaned_row: dict[str, Optional[str]] = {}
        for field in Location.model_fields.keys():
            value = row.get(field)
            if value is None:
                cleaned_row[field] = None
                continue
            value = value.strip()
            cleaned_row[field] = value if value != "" else None
        return cleaned_row

    def read(self) -> list[Location]:
        """Read the CSV file and return a list of Location objects.
        The CSV file must have the following columns:
        - city
        - country
        - state
        - postal_code
        Returns:
            list[Location]: A list of Location objects.
        """
        locations: list[Location] = []
        with open(self.file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cleaned_row = self._clean_row(row)
                try:
                    loc = Location(**cleaned_row)
                    locations.append(loc)
                except ValidationError as e:
                    print(f"Error parsing row: {row}")
                    print(f"Error: {e}")
                    continue
        return locations
            



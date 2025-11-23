"""CSV file writing utilities."""

import csv
from typing import Tuple

from weather_module.models.models import Location, WeatherData

class CSVWriter:
    """CSV file writing utilities."""
    def __init__(self, file_path: str, units: str = "C", detailed: bool = False):
        self.file_path = file_path
        self.units = units.upper()
        self.detailed = detailed

    def write(self, data: list[Tuple[Location, WeatherData]]):
        if not data:
            return

        temp_fields: list[str] = []
        if self.units in ("C", "BOTH", "ALL"):
            temp_fields.append("temp_c")
        if self.units in ("F", "BOTH", "ALL"):
            temp_fields.append("temp_f")
        if self.units in ("K", "ALL"):
            temp_fields.append("temp_k")

        fieldnames = [
            "country",
            "state",
            "city",
            "zip_code",
            *temp_fields,
            "clouds",
            "wind_speed_kph",
        ]
        
        if self.detailed:
            detailed_fields = [
                "wind_degree",
                "wind_dir",
                "pressure_mb",
                "pressure_in",
                "precip_mm",
                "precip_in",
                "humidity",
                "feelslike_c",
                "feelslike_f",
                "vis_km",
                "vis_miles",
                "uv",
                "gust_kph",
                "gust_mph",
                "last_updated",
            ]
            fieldnames.extend(detailed_fields)

        with open(self.file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for location, weather_data in data:
                row = {
                    "country": location.country or "",
                    "state": location.state or "",
                    "city": location.city or "",
                    "zip_code": location.zip_code or "",
                    "clouds": weather_data.clouds,
                    "wind_speed_kph": weather_data.wind_speed_kph,
                }

                if "temp_c" in temp_fields:
                    row["temp_c"] = "" if weather_data.temp_c is None else weather_data.temp_c
                if "temp_f" in temp_fields:
                    row["temp_f"] = "" if weather_data.temp_f is None else weather_data.temp_f
                if "temp_k" in temp_fields:
                    row["temp_k"] = "" if weather_data.temp_k is None else weather_data.temp_k

                if self.detailed:
                    row["wind_degree"] = "" if weather_data.wind_degree is None else weather_data.wind_degree
                    row["wind_dir"] = "" if weather_data.wind_dir is None else weather_data.wind_dir
                    row["pressure_mb"] = "" if weather_data.pressure_mb is None else weather_data.pressure_mb
                    row["pressure_in"] = "" if weather_data.pressure_in is None else weather_data.pressure_in
                    row["precip_mm"] = "" if weather_data.precip_mm is None else weather_data.precip_mm
                    row["precip_in"] = "" if weather_data.precip_in is None else weather_data.precip_in
                    row["humidity"] = "" if weather_data.humidity is None else weather_data.humidity
                    row["feelslike_c"] = "" if weather_data.feelslike_c is None else weather_data.feelslike_c
                    row["feelslike_f"] = "" if weather_data.feelslike_f is None else weather_data.feelslike_f
                    row["vis_km"] = "" if weather_data.vis_km is None else weather_data.vis_km
                    row["vis_miles"] = "" if weather_data.vis_miles is None else weather_data.vis_miles
                    row["uv"] = "" if weather_data.uv is None else weather_data.uv
                    row["gust_kph"] = "" if weather_data.gust_kph is None else weather_data.gust_kph
                    row["gust_mph"] = "" if weather_data.gust_mph is None else weather_data.gust_mph
                    row["last_updated"] = "" if weather_data.last_updated is None else weather_data.last_updated

                writer.writerow(row)

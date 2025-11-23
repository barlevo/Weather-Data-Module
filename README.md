# Weather Module

A Python-based weather data processing module that fetches weather information from WeatherAPI, processes it through a clean service layer, and provides multiple interfaces: CLI, Python API, and HTTP REST API.

## Features

- 🌡️ **Weather Data Fetching**: Get current weather data for cities worldwide
- 📊 **CSV Processing**: Read locations from CSV, fetch weather, write enriched results
- 💾 **Caching**: In-memory caching with configurable TTL (default 15 minutes)
- 🌐 **Multiple Interfaces**: CLI, Python API, and HTTP REST API
- 📦 **Detailed Data**: Optional detailed weather fields (pressure, humidity, UV, etc.)
- 🔄 **Bulk Operations**: Process multiple locations efficiently
- ⚙️ **Flexible Units**: Support for Celsius, Fahrenheit, Kelvin, or all units

## Project Structure

```
solid/
├── src/
│   └── weather_module/
│       ├── api/              # External WeatherAPI client
│       ├── cache/            # Caching layer
│       ├── http_api/         # FastAPI REST endpoints
│       ├── io/               # CSV reading/writing
│       ├── models/           # Data models (Location, WeatherData)
│       ├── services/         # Business logic layer
│       ├── cli.py            # Command-line interface
│       ├── config.py         # Configuration management
│       └── pipeline.py       # End-to-end processing pipeline
├── tests/                    # Test suite
├── csv_examples/             # Example CSV files
└── main.py                   # FastAPI entry point
```

## Installation

### Prerequisites

- Python 3.8 or higher
- WeatherAPI account and API key (get one at https://www.weatherapi.com/)

### Setup

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # On Windows PowerShell
   ```

3. **Install the package and dependencies**:
   
   Install the package in editable mode (this allows you to use the `weather-cli` command):
   ```powershell
   pip install -e .
   ```
   
   This will automatically install all dependencies from `requirements.txt` and set up the CLI command.
   
   **Alternative:** If you only want dependencies without the CLI command:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```env
   WEATHER_API_KEY=your_actual_api_key_here
   WEATHER_API_BASE_URL=https://api.weatherapi.com/v1
   CACHE_ENABLED=true
   CACHE_TTL_SECONDS=900
   ```
   
   Replace `your_actual_api_key_here` with your WeatherAPI key.

## Usage

### 1. Running with Python Command

You can use the pipeline directly in Python:

```python
from weather_module.pipeline import run_pipeline

run_pipeline(
    input_csv="csv_examples/example_locations.csv",
    output_csv="output.csv",
    units="C",
    detailed=True,
    use_cache=True,
    verbose=True
)
```

### 2. Running from CLI

The CLI provides a convenient command-line interface. There are two ways to run it:

#### Installation Method

**Option A: Using the CLI command (recommended)**
- Requires: `pip install -e .` (editable install)
- Command: `weather-cli run input.csv output.csv`

**Option B: Using Python module**
- Requires: Dependencies installed (`pip install -r requirements.txt`)
- Command: `python -m weather_module.cli run input.csv output.csv`

#### Basic Usage

```powershell
# Using the CLI command (after pip install -e .)
weather-cli run input.csv output.csv

# Or using Python module directly
python -m weather_module.cli run input.csv output.csv
```

#### CLI Options

All examples below use `weather-cli` (can be replaced with `python -m weather_module.cli`):

```powershell
# Use Fahrenheit instead of Celsius
weather-cli run input.csv output.csv --units F

# Include detailed weather data (pressure, humidity, UV, etc.)
weather-cli run input.csv output.csv --detailed

# Process only first 5 rows
weather-cli run input.csv output.csv --max-rows 5

# Disable caching
weather-cli run input.csv output.csv --no-cache

# Set custom cache TTL (in seconds)
weather-cli run input.csv output.csv --ttl 600

# Use bulk API endpoint (faster for multiple locations)
weather-cli run input.csv output.csv --bulk

# Verbose output
weather-cli run input.csv output.csv --verbose

# Combine multiple options
weather-cli run input.csv output.csv --units both --detailed --verbose --max-rows 3
```

#### Example

```powershell
# Process example locations with detailed data
weather-cli run csv_examples/example_locations.csv weather_output.csv --detailed --verbose
```

### 3. Using HTTP Endpoints

Start the FastAPI server:

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn weather_module.http_api:app --reload
```

The API will be available at `http://localhost:8000`

#### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Available Endpoints

##### GET `/weather/current`

Get current weather for a single location.

**Query Parameters:**
- `city` (optional): City name, e.g., "London"
- `country` (optional): Country name, e.g., "United Kingdom"
- `state` (optional): State/region name
- `zip_code` (optional): Zip code, e.g., "10001"
- `units` (optional, default: "C"): Temperature units - "C", "F", "K", "BOTH", "ALL"
- `detailed` (optional, default: false): Include detailed weather data

**Examples:**

```bash
# Basic request
curl "http://localhost:8000/weather/current?city=London"

# With country
curl "http://localhost:8000/weather/current?city=London&country=United%20Kingdom"

# With detailed data and Fahrenheit
curl "http://localhost:8000/weather/current?city=New%20York&units=F&detailed=true"

# Using zip code
curl "http://localhost:8000/weather/current?zip_code=10001&detailed=true"
```

**Response:**

```json
{
  "data": {
    "country": "United Kingdom",
    "state": "City of London, Greater London",
    "city": "London",
    "time_zone": "Europe/London",
    "temp_c": 10.1,
    "clouds": 25,
    "wind_speed_kph": 20.5,
    "wind_degree": 265,
    "pressure_mb": 998.0,
    "humidity": 66,
    ...
  },
  "message": "ok",
  "status": 200
}
```

##### POST `/weather/bulk`

Get current weather for multiple locations in a single request.

**Request Body:**

```json
{
  "locations": [
    {"city": "London", "country": "United Kingdom"},
    {"city": "Paris", "country": "France"},
    {"city": "New York", "country": "United States"}
  ]
}
```

**Query Parameters:**
- `units` (optional, default: "C"): Temperature units
- `detailed` (optional, default: false): Include detailed weather data

**Example:**

```bash
curl -X POST "http://localhost:8000/weather/bulk?detailed=true" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [
      {"city": "London", "country": "United Kingdom"},
      {"city": "Paris", "country": "France"}
    ]
  }'
```

##### GET `/health`

Health check endpoint.

```bash
curl http://localhost:8000/health
```

## Input CSV Format

Your input CSV file should have the following columns (all optional, but at least one should have data):

```csv
country,state,city,zip_code
United Kingdom,England,London,EC2Y 5AA
United States,New York,New York,10001
France,,Paris,75001
```

The CSV reader supports:
- Missing columns (they'll be set to None)
- Empty values (converted to None)
- Whitespace stripping

## Output CSV Format

### Basic Mode (default)

When `--detailed` flag is not used, the output CSV includes:
- `country`, `state`, `city`, `zip_code`
- Temperature fields (based on `--units` option)
- `clouds`, `wind_speed_kph`

### Detailed Mode (`--detailed` flag)

When `--detailed` is used, the output CSV includes all basic fields plus:
- `wind_degree`, `wind_dir`
- `pressure_mb`, `pressure_in`
- `precip_mm`, `precip_in`
- `humidity`
- `feelslike_c`, `feelslike_f`
- `vis_km`, `vis_miles`
- `uv`
- `gust_kph`, `gust_mph`
- `last_updated`

## Configuration

Configuration is managed through environment variables in `.env`:

```env
WEATHER_API_KEY=your_api_key_here
WEATHER_API_BASE_URL=https://api.weatherapi.com/v1
CACHE_ENABLED=true
CACHE_TTL_SECONDS=900
API_HOST=0.0.0.0
API_PORT=8000
```

## Testing

Run the test suite:

```powershell
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_api.py -v

# With coverage
pytest tests/ --cov=src/weather_module
```

## Architecture

The project follows clean architecture principles:

- **API Layer** (`api/`): External WeatherAPI client
- **Service Layer** (`services/`): Business logic, caching, unit conversion
- **HTTP Layer** (`http_api/`): FastAPI routes and dependencies
- **IO Layer** (`io/`): CSV reading/writing
- **Models** (`models/`): Data structures (Location, WeatherData)
- **CLI** (`cli.py`): Command-line interface
- **Pipeline** (`pipeline.py`): End-to-end processing orchestration


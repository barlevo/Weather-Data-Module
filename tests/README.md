# Testing Guide

## Test Structure

The test suite for the Weather API client includes:

1. **Mocked Tests** (`TestWeatherClientMocked`) - Fast unit tests with mocked HTTP responses
2. **Error Handling Tests** (`TestWeatherClientErrorHandling`) - Tests for various error scenarios
3. **Real API Tests** (`TestWeatherClientRealAPI`) - Integration tests with actual WeatherAPI
4. **Edge Cases** (`TestWeatherClientEdgeCases`) - Boundary conditions and edge cases

## Running Tests

### Install Test Dependencies

First, install the required packages:

```powershell
pip install -r requirements.txt
```

### Run All Tests

Run all tests (excluding integration tests):

```powershell
pytest tests/test_api.py -v
```

### Run Only Mocked Tests (Fast)

Run only mocked unit tests (no API calls):

```powershell
pytest tests/test_api.py::TestWeatherClientMocked -v
```

### Run Error Handling Tests

Test error scenarios:

```powershell
pytest tests/test_api.py::TestWeatherClientErrorHandling -v
```

### Run Integration Tests (Real API)

Run tests that make actual API calls (requires API key in `.env`):

```powershell
pytest tests/test_api.py::TestWeatherClientRealAPI -v -m integration
```

Or run all tests including integration:

```powershell
pytest tests/test_api.py -v -m integration
```

### Run Specific Test

Run a single test:

```powershell
pytest tests/test_api.py::TestWeatherClientMocked::test_get_current_weather_success -v
```

## Test Coverage

### Mocked Tests Include:
- ✅ Successful weather data retrieval
- ✅ Different cities (London, New York)
- ✅ Zip code queries
- ✅ Coordinate-based queries
- ✅ Custom timeout settings

### Error Handling Tests Include:
- ✅ HTTP 404 (Not Found)
- ✅ HTTP 401 (Unauthorized - invalid API key)
- ✅ HTTP 400 (Bad Request)
- ✅ HTTP 500 (Server Error)
- ✅ Network connection errors
- ✅ Timeout errors
- ✅ Invalid JSON responses
- ✅ Missing required fields in response

### Real API Tests Include:
- ✅ London weather data
- ✅ New York weather data
- ✅ Zip code queries
- ✅ Invalid city error handling

### Edge Cases Include:
- ✅ Client initialization defaults
- ✅ Custom base URLs
- ✅ Empty query strings

## Test Markers

Tests are marked for categorization:

- `@pytest.mark.integration` - Tests that require real API key
- No marker - Regular unit tests with mocks

## Example Output

When running tests, you should see:

```
tests/test_api.py::TestWeatherClientMocked::test_get_current_weather_success PASSED
tests/test_api.py::TestWeatherClientMocked::test_get_current_weather_different_city PASSED
tests/test_api.py::TestWeatherClientErrorHandling::test_get_current_weather_http_404_not_found PASSED
tests/test_api.py::TestWeatherClientRealAPI::test_get_current_weather_real_api_london PASSED
...
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
- Make sure you're running tests from the project root
- Or run: `pip install -e .` to install package in development mode

### Integration Tests Skipped
- Make sure `.env` file exists with valid `WEATHER_API_KEY`
- Integration tests will be skipped if API key is not configured

### Mock Tests Fail
- Check that all required fields are in mock responses
- Verify the WeatherData model matches the expected structure


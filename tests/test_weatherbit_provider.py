import pytest
import requests_mock
from app.integrations.weather import WeatherbitWeatherProvider
from app.integrations.weather import WeatherException
from app.api.models import WeatherItem
from app.conf.settings import settings


@pytest.fixture
def weather_provider():
    """Fixture to create a WeatherbitWeatherProvider instance."""
    return WeatherbitWeatherProvider()


def test_parse_address_success(weather_provider):
    """Test correct parsing of receiver address."""
    receiver_address = "Street 10, 75001 Paris, France"
    zip_code, country_code = weather_provider.parse_address(receiver_address)

    assert zip_code == "75001"
    assert country_code == "FR"


def test_parse_address_invalid_format(weather_provider):
    """Test handling of incorrectly formatted addresses."""
    with pytest.raises(Exception) as excinfo:
        weather_provider.parse_address("InvalidAddress")

    assert "Invalid address format" in str(excinfo.value)


def test_get_weather_success(weather_provider):
    """Integration test: Ensure Weatherbit API is called correctly & returns expected weather data."""
    receiver_address = "Street 10, 75001 Paris, France"

    # Expected mock response
    mock_response = {
        'data': [
            {'app_temp': 8.7, 'aqi': 82, 'city_name': 'Paris', 'clouds': 50, 'country_code': 'FR',
             'datetime': '2025-03-05:18', 'dewpt': 2.9, 'dhi': 0, 'dni': 0, 'elev_angle': -3.95, 'ghi': 0, 'gust': 3.6,
             'h_angle': -90, 'lat': 48.8534, 'lon': 2.3488, 'ob_time': '2025-03-05 18:02', 'pod': 'n', 'precip': 1,
             'pres': 1014, 'rh': 67, 'slp': 1020, 'snow': 0, 'solar_rad': 0,
             'sources': ['analysis', 'radar', 'satellite'], 'state_code': '11', 'station': 'C1292', 'sunrise': '06:22',
             'sunset': '17:42', 'temp': 8.7, 'timezone': 'Europe/Paris', 'ts': 1741197755, 'uv': 0, 'vis': 16,
             'weather': {'description': 'Light rain', 'code': 500, 'icon': 'r01n'}, 'wind_cdir': 'S',
             'wind_cdir_full': 'south', 'wind_dir': 187, 'wind_spd': 1.5}
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(settings.WEATHERBIT_API_URL, json=mock_response, status_code=200)

        weather = weather_provider.get_weather(receiver_address)

        assert isinstance(weather, WeatherItem)
        assert weather.wind == "south"
        assert weather.temp == 8.7
        assert weather.city == "Paris"
        assert weather.cloud == 50
        assert weather.description == "Light rain"


def test_get_weather_no_data(weather_provider):
    """Test API returns a valid response but no weather data."""
    receiver_address = "Street 10, 75001 Paris, France"

    mock_response = {"data": []}  # Empty data array

    with requests_mock.Mocker() as mocker:
        mocker.get(settings.WEATHERBIT_API_URL, json=mock_response, status_code=200)

        with pytest.raises(WeatherException) as excinfo:
            weather_provider.get_weather(receiver_address)

        assert "No data found" in str(excinfo.value)


def test_get_weather_api_failure(weather_provider):
    """Test handling of API failure (e.g., 500 error from Weatherbit)."""
    receiver_address = "Street 10, 75001 Paris, France"

    with requests_mock.Mocker() as mocker:
        mocker.get(settings.WEATHERBIT_API_URL, status_code=500)

        with pytest.raises(WeatherException) as excinfo:
            weather_provider.get_weather(receiver_address)

        assert "Failed to fetch weather data" in str(excinfo.value)

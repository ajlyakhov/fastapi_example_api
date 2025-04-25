import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.api.models import WeatherItem, TrackingItem
from app.db.dynamodb import DatabaseException
from app.integrations.weather import WeatherException
from app.main import app
from app.api.tracking import get_database, get_weather

client = TestClient(app)


@pytest.fixture
def mock_database():
    """Mock the database provider."""
    mock_db = MagicMock()

    mock_db.get_tracking_item.return_value = TrackingItem(**{
        "tracking_number": "TN12345678",
        "carrier": "DHL",
        "sender_address": "Street 1, 10115 Berlin, Germany",
        "receiver_address": "Street 10, 75001 Paris, France",
        "status": "in-transit",
        "articles": [
            {
                "article_name": "Laptop",
                "article_quantity": 1,
                "article_price": 800,
                "SKU": "LP123",
            },
            {
                "article_name": "Mouse",
                "article_quantity": 1,
                "article_price": 25,
                "SKU": "MO456",
            }
        ]
    })
    return mock_db


@pytest.fixture
def mock_weather_service():
    """Mock the weather service provider."""
    mock_weather = MagicMock()
    mock_weather.get_weather.return_value = WeatherItem(**{
        "wind": "south-southeast",
        "temp": 10,
        "city": "Paris",
        "cloud": 0,
        "description": "Clear sky"
    })
    return mock_weather


@pytest.fixture(autouse=True)
def override_dependencies(mock_database, mock_weather_service):
    """Override FastAPI dependencies with mock implementations."""
    app.dependency_overrides[get_database] = lambda: mock_database
    app.dependency_overrides[get_weather] = lambda: mock_weather_service
    yield
    app.dependency_overrides = {}  # Reset after tests


def test_track_shipment_success():
    """Test successful tracking request"""
    response = client.get("/track/DHL/TN12345678")

    assert response.status_code == 200
    json_data = response.json()
    assert "tracking" in json_data
    assert "weather" in json_data
    assert json_data["tracking"]["status"] == "in-transit"
    assert json_data["weather"]["temp"] == 10


def test_track_shipment_not_found(mock_database):
    """Test tracking number not found"""
    mock_database.get_tracking_item.return_value = None  # Simulate item not found

    response = client.get("/track/UPS/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Shipment not found"


def test_database_exception(mock_database):
    """Test database exception handling"""
    mock_database.get_tracking_item.side_effect = DatabaseException("Database error")

    response = client.get("/track/DHL/TN12345678")

    assert response.status_code == 500
    assert "Database exception" in response.json()["detail"]


def test_weather_exception(mock_weather_service):
    """Test weather service exception handling"""
    mock_weather_service.get_weather.side_effect = WeatherException("Weather API error")

    response = client.get("/track/DHL/TN12345678")

    assert response.status_code == 500
    assert "Weather exception" in response.json()["detail"]

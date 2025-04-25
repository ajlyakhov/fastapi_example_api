import re
from abc import ABC, abstractmethod
import requests
import pycountry
from requests import HTTPError

from app.api.models import WeatherItem
from app.conf.settings import settings
from app.integrations.cache import cache_weather


class WeatherException(Exception):
    """Base class for exceptions in this module."""

    pass


class WeatherProvider(ABC):
    """Abstract base class for weather providers."""

    @abstractmethod
    def get_weather(self, receiver_address: str) -> WeatherItem:
        pass


class WeatherbitWeatherProvider(WeatherProvider):
    """Weathebit weather data provider"""

    def __init__(self):
        self.api_key = settings.WEATHERBIT_API_KEY

    @staticmethod
    def parse_address(receiver_address: str):
        """Extract zip code and country code from normalized address string

        :param receiver_address:
        :return:
        """

        pattern = r'^(.*?),\s*([\w\d-]+)\s+([\w\s-]+),\s*([\w\s-]+)$'
        match = re.match(pattern, receiver_address)

        if match:
            street = match.group(1).strip()
            zip_code = match.group(2).strip()
            city = match.group(3).strip()
            country = match.group(4).strip()
            country_codes = pycountry.countries.search_fuzzy(country)
            if len(country_codes) > 0:
                country_code = country_codes[0].alpha_2
                return zip_code, country_code
            else:
                raise WeatherException("Country not found")
        else:
            raise WeatherException("Invalid address format")

    @cache_weather(expiration=settings.EXT_API_EXPIRATION)
    def call_weatherbit_api(self, zip_code: str, country_code: str) -> dict:
        """Call Weatherbit API using requests.

        :param zip_code: requested zip code
        :param country_code: requested country code (2-letter code)
        :return: JSON response from Weatherbit API
        """

        response = requests.get(
            settings.WEATHERBIT_API_URL,
            params={"postal_code": zip_code, "country": country_code, "key": self.api_key}
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def unify_weatherbit_data(weatherbit_data: dict) -> WeatherItem:
        """Unify weather data from Weatherbit to make compatible across all Weather providers"""

        return WeatherItem(
            wind=weatherbit_data["wind_cdir_full"],
            temp=weatherbit_data["temp"],
            city=weatherbit_data["city_name"],
            cloud=weatherbit_data["clouds"],
            description=weatherbit_data["weather"]["description"],
        )

    def get_weather(self, receiver_address: str) -> WeatherItem:
        """Retrieve weather using Weatherbit API

        :param receiver_address: normalized address string
        :return: WeatherItem structure
        """

        zip_code, country_code = WeatherbitWeatherProvider.parse_address(receiver_address)

        try:
            weatherbit_json = self.call_weatherbit_api(zip_code, country_code)
            weatherbit_data = weatherbit_json["data"][0]
            return WeatherbitWeatherProvider.unify_weatherbit_data(weatherbit_data)
        except HTTPError:
            raise WeatherException("Failed to fetch weather data")
        except IndexError:
            raise WeatherException("No data found")
        except Exception as e:
            raise WeatherException(f"Internal error")


class WeatherServiceFactory:
    """Factory class to create weather providers"""

    @staticmethod
    def get_provider(provider_name: str) -> WeatherProvider:
        """Get weather provider by provider name"""

        providers = {
            "weatherbit": WeatherbitWeatherProvider,
        }
        if provider_name not in providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return providers[provider_name]()

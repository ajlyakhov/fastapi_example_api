import os
import time
import json
import functools
import redis

from app.conf.settings import settings


redis_client = redis.Redis(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT,
                           db=settings.REDIS_CACHE_DB)


def cache_weather(expiration=settings.EXT_API_EXPIRATION):
    """Caching decorator based on redis and key=zip:country

    :param expiration: Expiration time in seconds. By default - 2 hours (7200 seconds) are cached.
    """

    def is_running_in_tests() -> bool:
        """Detect if the code is running inside pytest."""
        return "PYTEST_CURRENT_TEST" in os.environ

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, zip_code, country_code):
            """Caching decorator based on redis and key=zip:country"""

            # Ignore caching if we run in testing mode
            if is_running_in_tests():
                return func(self, zip_code, country_code)

            # We need to use country together with zip, because zip codes not unique between countries
            cache_key = f"weather:{zip_code}:{country_code}"

            cached_value = redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # No data in cache, call function
            result = func(self, zip_code, country_code)

            # save function output in cache
            redis_client.setex(cache_key, expiration, json.dumps(result))

            return result

        return wrapper

    return decorator

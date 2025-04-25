import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


if os.getenv("ENV") == "dev":
    load_dotenv(".env.dev")


class Settings(BaseSettings):
    """Project global settings"""

    # AWS Dynamodb
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-central-1")
    DYNAMODB_ENDPOINT: str = os.getenv("DYNAMODB_ENDPOINT", "")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    TRACKING_TABLE: str = os.getenv("TRACKING_TABLE", "Tracking")

    # AWS Cloudwatch
    AWS_LAMBDA_FUNCTION_NAME: str = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    AWS_CW_LOGGING_GROUP: str = os.getenv("AWS_CW_LOGGING_GROUP", "/aws/lambda/trackapi-lambda")

    # External Weather API
    WEATHERBIT_API_KEY: str = os.getenv("WEATHER_API_KEY", "701ad37e6f004f43899350e11eb23b17")
    WEATHERBIT_API_URL: str = os.getenv("WEATHER_API_URL", "https://api.weatherbit.io/v2.0/current")
    EXT_API_EXPIRATION: int = os.getenv("EXT_API_EXPIRATION", 7200)

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_CACHE_DB: int = os.getenv("REDIS_CACHE_DB", 0)


settings = Settings()

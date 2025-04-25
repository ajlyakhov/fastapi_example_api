from typing import List
from pydantic import BaseModel, Field, ConfigDict


class TrackingRequest(BaseModel):
    """Model representing tracking request"""

    tracking_number: str
    carrier: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tracking_number": "TN12345678",
                "carrier": "DHL"
            }
        }
    )


class ArticleItem(BaseModel):
    """Model representing single article inside tracking data."""

    article_name: str
    article_quantity: int
    article_price: float
    SKU: str


class TrackingItem(BaseModel):
    """Model representing tracking data."""

    tracking_number: str
    carrier: str
    sender_address: str
    receiver_address: str
    status: str
    articles: List[ArticleItem]


class WeatherItem(BaseModel):
    """Model representing unified weather data."""

    wind: str
    temp: float
    city: str
    cloud: int
    description: str


class TrackingResponse(BaseModel):
    """Model representing response on tracking request."""

    tracking: TrackingItem = Field(..., description="Tracking information")
    weather: WeatherItem = Field(..., description="Weather information in customers location")

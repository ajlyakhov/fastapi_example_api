from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Path, Depends
from fastapi.responses import JSONResponse

from app.api.models import TrackingRequest, TrackingResponse
from app.db.dynamodb import DatabaseException
from app.db.factory import DatabaseFactory
from app.integrations.weather import WeatherServiceFactory, WeatherException
from app.conf.logging import log_request

router = APIRouter()


def get_database():
    """Return the default database provider."""
    return DatabaseFactory.get_provider("dynamodb")


def get_weather():
    """Return the default weather provider."""
    return WeatherServiceFactory.get_provider("weatherbit")


@router.get("/track/{carrier}/{tracking_number}",
            response_class=JSONResponse,
            response_model=TrackingResponse,
            description='Retrieve shipment information by tracking number and carrier',
            response_description='Return the list of tracking records.',
            tags=['Public API'],
            )
@log_request()
async def get_tracking_info(
        request: Request,
        carrier: Annotated[
            str,
            Path(
                description="Shipping carrier code",
                openapi_examples={
                    "DHL Example": {
                        "summary": "DHL carrier",
                        "value": "DHL"
                    },
                    "FedEx Example": {
                        "summary": "UPS carrier",
                        "value": "UPS"
                    }
                }
            )
        ],
        tracking_number: Annotated[
            str,
            Path(
                description="Tracking number",
                openapi_examples={
                    "Example": {
                        "summary": "TN12345678",
                        "value": "TN12345678"
                    }
                }
            )
        ],
        database=Depends(get_database),
        weather=Depends(get_weather),
):
    """Endpoint to retrieve the shipment and articles information by tracking number and carrier,
    including weather conditions in customer's location.
    :param request: original request object, used by logging
    :param carrier: carrier name
    :param tracking_number: tracking number
    :param database: dependency injection of database
    :param weather: dependency injection of weather
    :return: TrackingResponse structure
    """

    request = TrackingRequest(carrier=carrier, tracking_number=tracking_number)
    try:
        tracking_data = database.get_tracking_item(request.tracking_number, request.carrier)
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=f"Database exception: {e}")

    if not tracking_data:
        raise HTTPException(status_code=404, detail="Shipment not found")

    try:
        weather_data = weather.get_weather(tracking_data.receiver_address)
    except WeatherException as e:
        raise HTTPException(status_code=500, detail=f"Weather exception: {e}")

    return TrackingResponse(tracking=tracking_data, weather=weather_data)

from fastapi import FastAPI
from mangum import Mangum

from app.api import tracking


# Main FastAPI object initialization
app = FastAPI(
    title="Track and Trace API",
    description="Track your shipment and local weather",
    version="0.0.1",
)

# API routers
app.include_router(tracking.router)


# Mangum Adapter for AWS Lambda
handler = Mangum(app, lifespan="off")

import functools
import logging
import uuid

import boto3
from watchtower import CloudWatchLogHandler
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import json

from app.conf.settings import settings


def is_lambda():
    return settings.AWS_LAMBDA_FUNCTION_NAME is not None and len(settings.AWS_LAMBDA_FUNCTION_NAME) > 0


def get_logger():
    # Setup logging for dev and lambda modes
    logger = logging.getLogger("trackapi")
    logger.setLevel(logging.INFO)

    # Use CloudWatch for structured logs
    if is_lambda():
        cloudwatch_handler = CloudWatchLogHandler(
            log_group_name=settings.AWS_CW_LOGGING_GROUP,
            log_stream_name=settings.AWS_LAMBDA_FUNCTION_NAME,
            boto3_client=boto3.client("logs"),
        )
        # Remove all default handlers (including LambdaLoggerHandler)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        # Attach CloudWatch handler
        cloudwatch_handler.setLevel(logging.DEBUG)
        logger.addHandler(cloudwatch_handler)
    else:
        # use console logging for non-lambda environments
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(module)s] %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def log_request():
    """Decorator to log request and response details"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # tracing id to link request with response
            trace_id = str(uuid.uuid4())
            logger = get_logger()

            try:
                # Capture Request details
                method = request.method
                url = str(request.url)
                headers = dict(request.headers)
                query_params = dict(request.query_params)

                # Log request body as request arguments if applicable
                if method in ["POST", "PUT", "PATCH"]:
                    body = await request.body()
                    try:
                        arguments = json.loads(body.decode("utf-8"))
                    except json.JSONDecodeError:
                        arguments = body.decode("utf-8")  # Fallback for raw text bodies
                else:
                    arguments = kwargs

                logger.debug({
                    "trace_id": trace_id,
                    "action": "request",
                    "arguments": arguments,
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "query": query_params,
                })

                # Call the actual endpoint function
                response = await func(request, *args, **kwargs)

            except HTTPException as http_exc:
                # Log HTTPException but re-raise it so FastAPI handles it correctly
                logger.warning({
                    "trace_id": trace_id,
                    "action": "error_response",
                    "status_code": http_exc.status_code,
                    "detail": http_exc.detail
                })
                raise  # Rethrow HTTPException to let FastAPI return the correct response

            except Exception as e:
                # Catch unexpected errors and return a 500 response
                logger.error({
                    "trace_id": trace_id,
                    "action": "error",
                    "details": f"Unexpected error in decorated function: {e}"
                })
                return JSONResponse(
                    content={"error": "Internal Server Error"},
                    status_code=500
                )

            # Capture Response details
            logger.debug({
                "trace_id": trace_id,
                "action": "response",
                "body": response,
            })

            return response

        return wrapper
    return decorator

from fastapi import APIRouter, status
from pydantic import BaseModel

health_router = APIRouter()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@health_router.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    Perform a health check on the service.

    Returns:
        HealthCheck: A simple health check response.
    """
    return HealthCheck(status="OK")

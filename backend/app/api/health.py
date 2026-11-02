"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report that the backend is running."""
    return HealthResponse(
        status="ok",
        service="contractai-testing-backend",
        version=__version__,
    )

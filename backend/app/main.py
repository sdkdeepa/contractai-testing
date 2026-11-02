"""FastAPI application entry point.

Run locally from the backend/ directory:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app import __version__
from app.api.health import router as health_router

app = FastAPI(
    title="ContractAI Testing API",
    description=(
        "Evaluates AI-to-AI exchanges between two fictional partner systems "
        "(WalletCo and PartnerBank) against a shared API integration contract."
    ),
    version=__version__,
)

app.include_router(health_router)

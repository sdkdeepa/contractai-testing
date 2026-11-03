"""FastAPI application entry point.

Run locally from the backend/ directory:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import __version__
from app.api.contract import router as contract_router
from app.api.health import router as health_router
from app.api.scenarios import router as scenarios_router
from app.contracts.contract import ContractLoadError
from app.scenarios.registry import ScenarioLoadError

app = FastAPI(
    title="ContractAI Testing API",
    description=(
        "Evaluates AI-to-AI exchanges between two fictional partner systems "
        "(WalletCo and PartnerBank) against a shared API integration contract."
    ),
    version=__version__,
)

app.include_router(health_router)
app.include_router(contract_router)
app.include_router(scenarios_router)


@app.exception_handler(ContractLoadError)
@app.exception_handler(ScenarioLoadError)
async def _data_file_error(_: Request, exc: Exception) -> JSONResponse:
    """A broken contract or scenario file is a server setup problem. Say so plainly."""
    return JSONResponse(
        status_code=500,
        content={"error": type(exc).__name__, "detail": str(exc)},
    )

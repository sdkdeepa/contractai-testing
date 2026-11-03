"""GET /scenarios: metadata for the five demo scenarios."""

from fastapi import APIRouter

from app.contracts.contract import load_contract
from app.scenarios.models import ScenarioList
from app.scenarios.registry import load_scenarios

router = APIRouter(tags=["scenarios"])


@router.get("/scenarios", response_model=ScenarioList)
def list_scenarios() -> ScenarioList:
    """Return scenario metadata. Fixture payloads are not included."""
    return ScenarioList(
        contract_version=load_contract().version,
        scenarios=[s.to_metadata() for s in load_scenarios()],
    )

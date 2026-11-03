"""GET /contract: human-readable summary of the shared contract."""

from fastapi import APIRouter

from app.contracts.contract import ContractSummary, load_contract

router = APIRouter(tags=["contract"])


@router.get("/contract", response_model=ContractSummary)
def get_contract() -> ContractSummary:
    """Return the contract's actions and clauses. No field lists or example data."""
    return load_contract().to_summary()

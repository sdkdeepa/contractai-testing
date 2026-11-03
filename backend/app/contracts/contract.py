"""Load and summarize the versioned WalletCo / PartnerBank contract."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from app.contracts.models import VERSION_PATTERN, ActionName, Scope, StrictModel

CONTRACT_PATH = Path(__file__).with_name("wallet_bank_contract.json")

CLAUSE_ID_PATTERN = r"^[A-Z]+-\d{2}$"

Layer = Literal["api_contract", "behavioral"]
EvaluationMethod = Literal["deterministic", "llm_judge"]


class ContractLoadError(RuntimeError):
    """Raised when the contract file is missing or invalid."""


class ActionSpec(StrictModel):
    name: ActionName
    description: str
    requires_authorization_scope: Scope | None
    request_required_fields: list[str]
    request_optional_fields: list[str]
    response_required_fields: list[str]
    response_optional_fields: list[str]


class Clause(StrictModel):
    id: str = Field(pattern=CLAUSE_ID_PATTERN)
    title: str
    rule: str
    layer: Layer
    evaluation_method: EvaluationMethod


class ContractDocument(StrictModel):
    """The full contract as stored in wallet_bank_contract.json."""

    contract_id: str
    version: str = Field(pattern=VERSION_PATTERN)
    title: str
    consumer: str
    provider: str
    summary: str
    data_policy: str
    actions: list[ActionSpec] = Field(min_length=1)
    clauses: list[Clause] = Field(min_length=1)

    @model_validator(mode="after")
    def _ids_are_unique(self) -> "ContractDocument":
        clause_ids = [c.id for c in self.clauses]
        duplicates = sorted({cid for cid in clause_ids if clause_ids.count(cid) > 1})
        if duplicates:
            raise ValueError(f"Duplicate clause IDs: {duplicates}")
        action_names = [a.name for a in self.actions]
        if len(action_names) != len(set(action_names)):
            raise ValueError(f"Duplicate action names: {action_names}")
        return self

    @property
    def clause_ids(self) -> set[str]:
        return {c.id for c in self.clauses}

    def to_summary(self) -> "ContractSummary":
        return ContractSummary(
            contract_id=self.contract_id,
            version=self.version,
            title=self.title,
            consumer=self.consumer,
            provider=self.provider,
            summary=self.summary,
            data_policy=self.data_policy,
            actions=[
                ActionSummary(
                    name=a.name,
                    description=a.description,
                    requires_authorization_scope=a.requires_authorization_scope,
                )
                for a in self.actions
            ],
            clauses=[ClauseSummary(**c.model_dump()) for c in self.clauses],
        )


# --- Public, human-readable summary (served by GET /contract) ------------------
# Contains descriptions and rules only: no field lists, no example payloads,
# and never any card data.


class ActionSummary(StrictModel):
    name: ActionName
    description: str
    requires_authorization_scope: Scope | None


class ClauseSummary(StrictModel):
    id: str
    title: str
    rule: str
    layer: Layer
    evaluation_method: EvaluationMethod


class ContractSummary(StrictModel):
    contract_id: str
    version: str
    title: str
    consumer: str
    provider: str
    summary: str
    data_policy: str
    actions: list[ActionSummary]
    clauses: list[ClauseSummary]


@lru_cache
def load_contract(path: Path = CONTRACT_PATH) -> ContractDocument:
    """Read and validate the contract file. Cached after the first call."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractLoadError(f"Contract file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractLoadError(f"Contract file is not valid JSON: {path}: {exc}") from exc

    try:
        return ContractDocument.model_validate(raw)
    except ValidationError as exc:
        raise ContractLoadError(f"Contract file failed validation: {path}\n{exc}") from exc

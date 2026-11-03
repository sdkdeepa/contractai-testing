"""The contract file is valid and matches the Pydantic models."""

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from app.contracts.contract import CONTRACT_PATH, ContractLoadError, load_contract
from app.contracts.models import (
    EligibilityRequest,
    EligibilityResponse,
    ProvisionRequest,
    ProvisionResponse,
)

REQUIRED_CLAUSES = {
    "ACT-01",    # allowed actions
    "SHAPE-01",  # request shapes
    "SHAPE-02",  # response shapes
    "AUTH-01",   # provisioning requires authorization
    "SEM-01",    # eligibility has no side effects
    "SEM-02",    # eligibility is not described as activation
    "PRIV-01",   # no raw card data
    "SEC-01",    # untrusted text cannot override policy
}

MODELS_BY_ACTION: dict[str, tuple[type[BaseModel], type[BaseModel]]] = {
    "check_eligibility": (EligibilityRequest, EligibilityResponse),
    "provision_token": (ProvisionRequest, ProvisionResponse),
}


def _required(model: type[BaseModel]) -> set[str]:
    return {name for name, f in model.model_fields.items() if f.is_required()}


def _optional(model: type[BaseModel]) -> set[str]:
    return {name for name, f in model.model_fields.items() if not f.is_required()}


def test_contract_loads_with_semver_version() -> None:
    contract = load_contract()
    assert contract.version == "1.0.0"
    assert contract.consumer == "WalletCo"
    assert contract.provider == "PartnerBank"


def test_contract_has_exactly_the_required_clauses() -> None:
    assert load_contract().clause_ids == REQUIRED_CLAUSES


def test_contract_defines_exactly_two_actions() -> None:
    names = {a.name for a in load_contract().actions}
    assert names == {"check_eligibility", "provision_token"}


def test_only_provisioning_requires_authorization() -> None:
    scopes = {a.name: a.requires_authorization_scope for a in load_contract().actions}
    assert scopes == {"check_eligibility": None, "provision_token": "token:provision"}


def test_shape_clauses_are_api_contract_layer_and_others_are_behavioral() -> None:
    layers = {c.id: c.layer for c in load_contract().clauses}
    api_layer = {cid for cid, layer in layers.items() if layer == "api_contract"}
    assert api_layer == {"ACT-01", "SHAPE-01", "SHAPE-02"}


def test_only_semantic_interpretation_uses_llm_judge() -> None:
    methods = {c.id: c.evaluation_method for c in load_contract().clauses}
    judged = {cid for cid, method in methods.items() if method == "llm_judge"}
    assert judged == {"SEM-02"}


@pytest.mark.parametrize("action", sorted(MODELS_BY_ACTION))
def test_contract_field_lists_match_pydantic_models(action: str) -> None:
    spec = next(a for a in load_contract().actions if a.name == action)
    request_model, response_model = MODELS_BY_ACTION[action]

    assert set(spec.request_required_fields) == _required(request_model)
    assert set(spec.request_optional_fields) == _optional(request_model)
    assert set(spec.response_required_fields) == _required(response_model)
    assert set(spec.response_optional_fields) == _optional(response_model)


def test_summary_excludes_field_lists() -> None:
    summary = load_contract().to_summary().model_dump_json()
    assert "request_required_fields" not in summary
    assert "response_required_fields" not in summary


def test_duplicate_clause_ids_give_a_clear_error(tmp_path: Path) -> None:
    raw = json.loads(CONTRACT_PATH.read_text())
    raw["clauses"].append(dict(raw["clauses"][0]))
    bad = tmp_path / "contract.json"
    bad.write_text(json.dumps(raw))

    with pytest.raises(ContractLoadError, match="Duplicate clause IDs"):
        load_contract.__wrapped__(bad)


def test_missing_contract_file_gives_a_clear_error(tmp_path: Path) -> None:
    with pytest.raises(ContractLoadError, match="not found"):
        load_contract.__wrapped__(tmp_path / "missing.json")

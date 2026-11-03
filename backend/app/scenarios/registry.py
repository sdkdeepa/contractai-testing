"""Load scenario definitions and check them against the contract."""

import json
from functools import lru_cache
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from app.contracts.contract import ContractDocument, load_contract
from app.scenarios.models import Scenario

SCENARIOS_PATH = Path(__file__).with_name("scenarios.json")

_scenario_list = TypeAdapter(list[Scenario])


class ScenarioLoadError(RuntimeError):
    """Raised when the scenarios file is missing, invalid, or inconsistent with the contract."""


def _check_against_contract(scenarios: list[Scenario], contract: ContractDocument) -> None:
    ids = [s.id for s in scenarios]
    if len(ids) != len(set(ids)):
        raise ScenarioLoadError(f"Duplicate scenario IDs: {ids}")

    for scenario in scenarios:
        unknown = sorted(set(scenario.clause_ids) - contract.clause_ids)
        if unknown:
            raise ScenarioLoadError(
                f"Scenario {scenario.id} references unknown clause IDs: {unknown}"
            )
        for exchange in scenario.fixture.transcript:
            version = exchange.request.contract_version
            if version != contract.version:
                raise ScenarioLoadError(
                    f"Scenario {scenario.id} request {exchange.request.request_id} uses "
                    f"contract_version {version}, expected {contract.version}"
                )


@lru_cache
def load_scenarios(path: Path = SCENARIOS_PATH) -> tuple[Scenario, ...]:
    """Read, validate, and cross-check all scenarios. Cached after the first call."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ScenarioLoadError(f"Scenarios file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ScenarioLoadError(f"Scenarios file is not valid JSON: {path}: {exc}") from exc

    try:
        scenarios = _scenario_list.validate_python(raw)
    except ValidationError as exc:
        raise ScenarioLoadError(f"Scenarios file failed validation: {path}\n{exc}") from exc

    _check_against_contract(scenarios, load_contract())
    return tuple(scenarios)

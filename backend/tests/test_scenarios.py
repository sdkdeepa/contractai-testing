"""Scenarios S1-S5 are complete, reference real clauses, and use synthetic data."""

import json
import re
from pathlib import Path

import pytest

from app.contracts.contract import load_contract
from app.scenarios.registry import SCENARIOS_PATH, ScenarioLoadError, load_scenarios

EXPECTED_IDS = ["S1", "S2", "S3", "S4", "S5"]

EXPECTED_FAILED_CLAUSES = {
    "S1": [],
    "S2": ["AUTH-01"],
    "S3": ["SEM-02"],
    "S4": ["AUTH-01", "SEM-01", "SEC-01"],
    "S5": ["PRIV-01"],
}

# The one raw card number allowed anywhere in the fixtures: the public test
# number, used only by S5 to demonstrate disclosure.
PUBLIC_TEST_PAN = "4111111111111111"
CARD_NUMBER_LIKE = re.compile(r"(?:\d[ -]?){13,19}")


def test_exactly_five_scenarios_in_order() -> None:
    assert [s.id for s in load_scenarios()] == EXPECTED_IDS


def test_every_scenario_has_plain_english_text() -> None:
    for s in load_scenarios():
        for text in (s.title, s.description, s.consumer_goal, s.expected_behavior):
            assert text.strip(), f"{s.id} has an empty text field"


def test_every_clause_reference_exists_in_the_contract() -> None:
    known = load_contract().clause_ids
    for s in load_scenarios():
        assert set(s.clause_ids) <= known, s.id
        assert set(s.expected_outcome.failed_clause_ids) <= set(s.clause_ids), s.id


@pytest.mark.parametrize("scenario_id", EXPECTED_IDS)
def test_expected_failed_clauses(scenario_id: str) -> None:
    scenario = next(s for s in load_scenarios() if s.id == scenario_id)
    assert scenario.expected_outcome.failed_clause_ids == EXPECTED_FAILED_CLAUSES[scenario_id]


def test_every_fixture_passes_the_api_contract_layer() -> None:
    """The project's core point: every fixture is schema-valid, even the failing ones."""
    for s in load_scenarios():
        assert s.expected_outcome.api_contract == "PASS", s.id


def test_only_s1_is_expected_to_pass_overall() -> None:
    passing = [s.id for s in load_scenarios() if s.expected_outcome.overall == "PASS"]
    assert passing == ["S1"]


def test_fixtures_are_labeled_deterministic() -> None:
    for s in load_scenarios():
        assert s.fixture.source == "deterministic_fixture"


def test_each_response_answers_its_own_request() -> None:
    for s in load_scenarios():
        for exchange in s.fixture.transcript:
            assert exchange.response.action == exchange.request.action, s.id
            assert exchange.response.request_id == exchange.request.request_id, s.id


def test_raw_card_numbers_appear_only_in_s5() -> None:
    for s in load_scenarios():
        text = s.fixture.model_dump_json()
        found = {re.sub(r"[ -]", "", m) for m in CARD_NUMBER_LIKE.findall(text)}
        if s.id == "S5":
            assert found == {PUBLIC_TEST_PAN}
        else:
            assert not found, f"{s.id} contains card-number-like data: {found}"


def test_unknown_clause_reference_gives_a_clear_error(tmp_path: Path) -> None:
    raw = json.loads(SCENARIOS_PATH.read_text())
    raw[0]["clause_ids"].append("FAKE-99")
    bad = tmp_path / "scenarios.json"
    bad.write_text(json.dumps(raw))

    with pytest.raises(ScenarioLoadError, match="unknown clause IDs: \\['FAKE-99'\\]"):
        load_scenarios.__wrapped__(bad)


def test_wrong_contract_version_gives_a_clear_error(tmp_path: Path) -> None:
    raw = json.loads(SCENARIOS_PATH.read_text())
    raw[0]["fixture"]["transcript"][0]["request"]["contract_version"] = "2.0.0"
    bad = tmp_path / "scenarios.json"
    bad.write_text(json.dumps(raw))

    with pytest.raises(ScenarioLoadError, match="expected 1.0.0"):
        load_scenarios.__wrapped__(bad)

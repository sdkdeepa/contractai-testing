"""Scenario definitions and the public metadata served by GET /scenarios."""

from typing import Literal

from pydantic import Field, model_validator

from app.contracts.models import Exchange, StrictModel

Verdict = Literal["PASS", "FAIL"]
FixtureSource = Literal["deterministic_fixture"]

SCENARIO_ID_PATTERN = r"^S[1-9]$"

# Shown wherever fixture output is displayed, so recorded messages are never
# mistaken for live AI output.
FIXTURE_LABEL = "Deterministic fixture: recorded synthetic messages, not live AI output."


class ExpectedOutcome(StrictModel):
    """What the evaluator should report for this scenario's fixture."""

    api_contract: Verdict
    behavioral: Verdict
    overall: Verdict
    failed_clause_ids: list[str]

    @model_validator(mode="after")
    def _is_consistent(self) -> "ExpectedOutcome":
        worst = "FAIL" if "FAIL" in (self.api_contract, self.behavioral) else "PASS"
        if self.overall != worst:
            raise ValueError(
                f"overall must be {worst} when api_contract={self.api_contract} "
                f"and behavioral={self.behavioral}"
            )
        if (self.overall == "PASS") != (not self.failed_clause_ids):
            raise ValueError("failed_clause_ids must be empty exactly when overall is PASS")
        return self


class ScenarioFixture(StrictModel):
    source: FixtureSource
    transcript: list[Exchange] = Field(min_length=1)


class Scenario(StrictModel):
    id: str = Field(pattern=SCENARIO_ID_PATTERN)
    title: str
    description: str
    consumer_goal: str
    expected_behavior: str
    clause_ids: list[str] = Field(min_length=1)
    fixture: ScenarioFixture
    expected_outcome: ExpectedOutcome

    @model_validator(mode="after")
    def _failed_clauses_are_relevant(self) -> "Scenario":
        unlisted = sorted(set(self.expected_outcome.failed_clause_ids) - set(self.clause_ids))
        if unlisted:
            raise ValueError(
                f"Scenario {self.id}: failed_clause_ids {unlisted} are not in clause_ids"
            )
        return self

    def to_metadata(self) -> "ScenarioMetadata":
        return ScenarioMetadata(
            id=self.id,
            title=self.title,
            description=self.description,
            consumer_goal=self.consumer_goal,
            expected_behavior=self.expected_behavior,
            clause_ids=self.clause_ids,
            expected_outcome=self.expected_outcome,
            fixture_source=self.fixture.source,
            fixture_label=FIXTURE_LABEL,
            exchange_count=len(self.fixture.transcript),
        )


class ScenarioMetadata(StrictModel):
    """Public description of a scenario. Excludes the fixture payloads."""

    id: str
    title: str
    description: str
    consumer_goal: str
    expected_behavior: str
    clause_ids: list[str]
    expected_outcome: ExpectedOutcome
    fixture_source: FixtureSource
    fixture_label: str
    exchange_count: int


class ScenarioList(StrictModel):
    contract_version: str
    scenarios: list[ScenarioMetadata]

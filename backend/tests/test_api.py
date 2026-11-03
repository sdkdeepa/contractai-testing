"""GET /contract and GET /scenarios."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_contract_returns_summary() -> None:
    response = client.get("/contract")

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "1.0.0"
    assert body["consumer"] == "WalletCo"
    assert body["provider"] == "PartnerBank"
    assert [a["name"] for a in body["actions"]] == ["check_eligibility", "provision_token"]
    assert {c["id"] for c in body["clauses"]} >= {"AUTH-01", "SEM-02", "PRIV-01", "SEC-01"}
    for clause in body["clauses"]:
        assert set(clause) == {"id", "title", "rule", "layer", "evaluation_method"}


def test_get_scenarios_returns_five_with_metadata() -> None:
    response = client.get("/scenarios")

    assert response.status_code == 200
    body = response.json()
    assert body["contract_version"] == "1.0.0"
    assert [s["id"] for s in body["scenarios"]] == ["S1", "S2", "S3", "S4", "S5"]
    for s in body["scenarios"]:
        assert s["fixture_source"] == "deterministic_fixture"
        assert "not live AI output" in s["fixture_label"]
        assert s["expected_outcome"]["api_contract"] == "PASS"


def test_get_scenarios_does_not_expose_fixture_payloads() -> None:
    text = client.get("/scenarios").text
    assert '"fixture"' not in text
    assert '"transcript"' not in text
    assert "4111 1111 1111 1111" not in text


def test_both_endpoints_are_in_the_openapi_schema() -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert {"/health", "/contract", "/scenarios"} <= set(paths)

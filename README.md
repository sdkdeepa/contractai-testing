# ContractAI Testing

An open-source portfolio MVP showing that two AI-enabled systems can agree on an API schema and still break the integration.

Two fictional partner systems exchange messages through AI agents:

- **WalletCo** (consumer)
- **PartnerBank** (provider)

Every message can be schema-valid and still violate the contract's meaning, authorization rules, or privacy rules. This project evaluates both layers separately:

| Layer | Question it answers | How |
|---|---|---|
| Traditional API contract validation | Does the payload match the schema? | Deterministic |
| AI behavioral evaluation | Did the agents respect authorization, privacy, and meaning? | Deterministic rules, plus an LLM judge for semantics |

An LLM judge can never override a deterministic failure.

All data is synthetic. There are no real banking credentials, card numbers, or payment APIs.

> **Status:** early development. The contract and scenarios are defined; the evaluator is not built yet. See [docs/handoff.md](docs/handoff.md).

## The contract

WalletCo and PartnerBank share a versioned contract, [`wallet_bank_contract.json`](backend/app/contracts/wallet_bank_contract.json). It defines two actions:

- `check_eligibility`: can this card be added to a wallet? Read-only.
- `provision_token`: issue an opaque wallet token. Needs customer authorization.

Each rule has a clause ID, such as `AUTH-01` (provisioning requires authorization) or `PRIV-01` (no raw card data), so every result can point to the exact rule it checked.

## Scenarios

| ID | Scenario | What goes wrong |
|---|---|---|
| S1 | Successful AI-to-AI handoff | Nothing |
| S2 | Missing authorization | Token issued without the right scope |
| S3 | Semantic misunderstanding | Eligibility check described as activation |
| S4 | Prompt injection attempt | Text in a customer note makes the bank provision a token |
| S5 | Sensitive-data exposure | Full card number in an agent message |

Every scenario's messages pass schema validation. Only the behavioral checks catch the problems.

Scenarios currently use deterministic fixtures: recorded, synthetic messages. They are labeled as such and are never presented as live AI output.

## Project structure

```
contractai-testing/
  backend/          Python FastAPI backend
    app/
      api/          HTTP routes only
      runner/       Scenario runner (orchestrates agents + evaluator)
      agents/       WalletCo and PartnerBank agent simulation
      contracts/    Shared, versioned contract (JSON) and Pydantic message models
      evaluator/    Contract validation and AI behavioral evaluation
      scenarios/    Scenarios S1-S5 with deterministic, synthetic fixtures
    tests/          pytest tests
  frontend/         React + TypeScript (added in a later step)
  docs/             Project notes and handoff
```

## Requirements

- Python 3.11 or newer
- Node.js and npm (needed once the frontend is added)

## Run the backend

From the `backend/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open these in your browser:

| URL | What it shows |
|---|---|
| http://127.0.0.1:8000/health | `"status": "ok"` when the backend is running |
| http://127.0.0.1:8000/contract | The contract's actions and clauses |
| http://127.0.0.1:8000/scenarios | The five scenarios and their expected outcomes |
| http://127.0.0.1:8000/docs | Interactive API docs |

## Run the backend tests

From the `backend/` directory, with the virtual environment active:

```bash
pytest
```

## License

MIT. See [LICENSE](LICENSE).

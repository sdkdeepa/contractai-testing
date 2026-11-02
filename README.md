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

> **Status:** early development. Step 1 of 8 (project skeleton) is complete. See [docs/handoff.md](docs/handoff.md).

## Planned scenarios

1. Successful AI-to-AI handoff
2. Missing authorization
3. Semantic misunderstanding (eligibility check interpreted as activation)
4. Prompt injection attempt
5. Sensitive-data exposure

## Project structure

```
contractai-testing/
  backend/          Python FastAPI backend
    app/
      api/          HTTP routes only
      runner/       Scenario runner (orchestrates agents + evaluator)
      agents/       WalletCo and PartnerBank agent simulation
      contracts/    Shared, versioned API integration contract
      evaluator/    Contract validation and AI behavioral evaluation
      scenarios/    Deterministic, synthetic fixtures
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

Then open http://127.0.0.1:8000/health. You should see `"status": "ok"`.

Interactive API docs are at http://127.0.0.1:8000/docs.

## Run the backend tests

From the `backend/` directory, with the virtual environment active:

```bash
pytest
```

## License

MIT. See [LICENSE](LICENSE).

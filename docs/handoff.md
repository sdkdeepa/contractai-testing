# Handoff

Concise state of the project. Updated at the end of every step.

## Current state

**Last completed:** Step 1 of 8, project skeleton (2026-10-31)

**Works today:**
- FastAPI backend starts and serves `GET /health`.
- One pytest test passes. Fresh install from `requirements.txt` verified.

**Not built yet:** contract, scenarios, agents, evaluator, runner logic, frontend, Live AI Mode.

## Decisions

- Repo: `contractai-testing`, MIT license, open source.
- Backend: Python 3.11+, FastAPI, pip + `requirements.txt`, pytest.
- Frontend: Vite + React + TypeScript, npm, Vitest.
- No database, Kubernetes, cloud infra, real payment APIs, or complex auth.
- Synthetic data only.
- Fixture Demo Mode first (deterministic, labeled as recorded). Live AI Mode later, optional, backend-only API key.
- Deterministic checks for schema, authorization, privacy. LLM judge for semantics only. An LLM can never override a deterministic failure.
- Simulated agent responses are never presented as live AI output.

## Architecture boundaries

- `frontend/` talks to the backend over HTTP only.
- `app/api/` holds routes only.
- `app/runner/` is the only module that imports both `agents` and `evaluator`.
- `app/agents/` never imports `evaluator`; `app/evaluator/` never imports `agents`.
- Agents do not call each other directly. The runner relays messages and captures the transcript.

## Scenarios (required, five)

1. Successful AI-to-AI handoff
2. Missing authorization
3. Semantic misunderstanding (eligibility check interpreted as activation)
4. Prompt injection attempt
5. Sensitive-data exposure

## Step plan

1. Skeleton. **Done.**
2. Shared versioned contract, transcript model, scenario fixtures
3. Deterministic checkers
4. Evaluation pipeline and verdict precedence
5. API endpoints
6. React frontend
7. Live AI Mode
8. README polish, demo script, final handoff

## Open items

- LLM provider for Live AI Mode (needed by Step 7).
- Developed with Python 3.13; 3.11 compatibility not yet run.
- Git repository not initialized; owner will create and push.

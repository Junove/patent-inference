# patent-inference

Patent inference framework using NEAR AI cloud TEE.

A local app, run in a browser tab, that drafts, searches and lints patent applications. A Python backend does the work; a Vite + React frontend drives it. Inference runs on Near AI Cloud.

- Generate a patent document (.docx) from uploaded documents, images and reference files, with live streamed progress.
- Search prior art through an HTTP API and an MCP tool (a seeded SQLite database stands in for a real patent source).
- Lint a patent file against the USPTO application structure, with a client-side document preview.

Full requirements: [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

## Repository layout

```
backend/             Python (FastAPI, SQLAlchemy, Alembic, pytest)
frontend/            Vite + React + TypeScript, MUI, TanStack Query, Vitest
packages/shared/      Shared TypeScript utilities (npm workspace)
packages/contracts/   API contract constants and types (npm workspace)
contract/             openapi.yaml, the API contract both sides share
demo/                 Sample .docx/source files and a slide deck for demoing the app
docs/                 Requirements and design notes
.github/              CI workflows
```

## Setup

Requirements: [uv](https://docs.astral.sh/uv/) (manages Python 3.11+ for the backend) and Node 20+.

Backend (from `backend/`):

```bash
cp ../.env.example .env   # add the Near AI Cloud key; never commit .env
uv run alembic upgrade head
uv run python -m app.search.seed   # seeds the patent search database
uv run pytest
uv run uvicorn app.main:app --reload
```

`uv run` creates and updates `.venv` automatically from `pyproject.toml`/`uv.lock`; no manual venv activation needed.

Run the patent search MCP server standalone:

```bash
uv run python -m app.search.mcp_server
```

Frontend (from the repository root):

```bash
npm run setup   # one command: npm ci, installs every workspace from package-lock.json
npm test        # runs vitest run in each workspace
npm run dev     # starts the Vite dev server against a real backend on :8000
npm run dev --workspace @near-private-ai/frontend -- --mode mock   # ...or against a mocked backend, no server needed
```

Regenerate the typed API client after changing `contract/openapi.yaml` with `npm run generate:api`.

CI runs `npm ci` followed by `npm test` from the repository root for the
frontend, and `uv run pytest` from `backend/`.

## Secrets

The Near AI Cloud key lives only in the backend's environment (`.env`, git-ignored). Share it through a password manager or GitHub Actions secrets. Never commit it, log it, or send it to the frontend. The backend process caches `.env` at startup, so restart it after changing the key.

## CORS

The frontend and backend run as separate origins (`:5173` and `:8000` by default), so the backend enables CORS for the frontend's origin via the `CORS_ORIGINS` env var (comma-separated).

## Working together

- `main` is protected. Every change goes through a pull request.
- Branch from `main` with short-lived branches such as `backend/search-api` or `frontend/linter-ui`.
- The API contract in `contract/openapi.yaml` is the only coupling between backend and frontend. Changes to it need approval from both collaborators.
- Pull requests run CI: pytest for the backend and Vitest for the frontend. Both must pass before merging.
- Work is tracked in GitHub issues, one per area in the requirements work split. Each issue lists the requirement IDs it covers (FR-..., NFR-...).

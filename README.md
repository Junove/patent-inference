# patent-inference

Patent inference framework using NEAR AI cloud TEE.

A local app, run in a browser tab, that drafts, searches and lints patent applications. A Python backend does the work; a Vite + React frontend drives it. Inference runs on Near AI Cloud.

- Generate a patent document (.docx) from uploaded documents, images and reference files.
- Search prior art through an HTTP API and an MCP tool (a seeded SQLite database stands in for a real patent source).
- Lint a patent file against the USPTO application structure.

Full requirements: [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

## Repository layout

```
backend/     Python (FastAPI, SQLAlchemy, Alembic, pytest)       owner: Collaborator A
frontend/    Vite + React + TypeScript, Vitest                   owner: Collaborator B
contract/    openapi.yaml, the API contract both sides share
docs/        Requirements and design notes
.github/     CI workflows
```

`backend/` and `frontend/` do not exist yet; they are scaffolded in phase 1 (see the issues).

## Setup

Requirements: Python 3.11+ and Node 20+.

Backend (from `backend/`):

```bash
pip install -r requirements.txt
cp ../.env.example .env   # add the Near AI Cloud key; never commit .env
pytest
```

Frontend (from `frontend/`):

```bash
npm ci
npm test
```

CI expects these conventions: `backend/requirements.txt` includes pytest, and `frontend/package.json` has a `test` script that runs `vitest run`.

## Secrets

The Near AI Cloud key lives only in the backend's environment (`.env`, git-ignored). Share it through a password manager or GitHub Actions secrets. Never commit it, log it, or send it to the frontend.

## Working together

- `main` is protected. Every change goes through a pull request.
- Branch from `main` with short-lived branches such as `backend/search-api` or `frontend/linter-ui`.
- The API contract in `contract/openapi.yaml` is the only coupling between backend and frontend. Changes to it need approval from both collaborators.
- Pull requests run CI: pytest for the backend and Vitest for the frontend. Both must pass before merging.
- Work is tracked in GitHub issues, one per area in the requirements work split. Each issue lists the requirement IDs it covers (FR-..., NFR-...).

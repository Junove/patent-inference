# Patent Inference: Requirements Specification

As of 2026-11-11

## Overview

Patent Inference is a local application that drafts, searches and lints patent applications, using hosted AI inference on Near AI Cloud. Two collaborators build it in parallel: one owns the Python backend, one owns the Vite + React frontend.

**Goals**

- Generate a patent document from raw user-supplied documents, images and reference files.
- Search prior art through a patent search API, mocked with a seeded database until real access exists.
- Lint a patent file (probably .docx) for structure and required sections.
- Give users one local UI for all three tools.

**Out of scope for v1**

- Filing with a patent office, multi-user accounts, and real patent database ingestion.

**Assumptions**

- Real patent database access is unavailable, so a seeded SQLite database stands in behind the same interface.
- SQLite is the v1 store; AWS RDS is a later swap, so data access must not depend on SQLite-specific features.
- One shared Near AI Cloud API key, funded with account credits, is used for all inference.
- "Desktop" is a browser tab: the React app runs locally against a local backend, with no Tauri or Electron wrapper in v1.

## Architecture

The frontend is a thin client: it never calls Near AI Cloud, the database or the disk directly. That keeps the API key on the backend and makes the REST contract the only coupling between the two collaborators.

```
 React frontend (Vite)  <-- REST + SSE -->  Python backend (FastAPI)  --HTTPS-->  Near AI Cloud
 Collaborator B                             Collaborator A            |
  - Search workspace                         - Generator jobs + .docx |-->  SQLite (AWS RDS later)
  - Linter workspace                         - Search API + MCP tool  |
  - Generator workspace                      - Linter rule engine     `-->  Local disk (uploads, outputs)
                                             - Uploads + extraction
```

The backend streams generation progress to the UI over server-sent events (SSE). Moving from SQLite to AWS RDS changes only the backend's database connection.

## Functional requirements

The app has four capabilities: patent search, patent linting, patent generation from uploads, and a local UI that drives all three. Priority: M = must have for v1, S = should have, C = could have.

### Patent search (FR-S)

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-S1 | Keyword search over patent title, abstract, claims and inventors, returning ranked results. | M |
| FR-S2 | Filters for date range, assignee, inventor and classification code. | S |
| FR-S3 | Result detail view with full text, claims and cited patents. | M |
| FR-S4 | Search is exposed as an HTTP API and as an MCP tool, so the generator and external agents can call it. | M |
| FR-S5 | Data sits behind a repository interface; the seeded SQLite database is the v1 implementation and a real patent source can replace it without API changes. | M |
| FR-S6 | A seed script loads a reproducible, clearly fake sample corpus (at least a few hundred records for development, plus a generator that produces 100,000 synthetic records for scale testing) covering several technology areas. | M |

### Patent linter (FR-L)

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-L1 | Accept freeform input: .docx and other documents, .pdf, plain text, and XML. Parse structure (headings, numbered paragraphs, claims, drawings references) where the format allows. | M |
| FR-L2 | Check required sections are present and in order: title, abstract, background, summary, drawings description, detailed description, claims, following the USPTO application format. | M |
| FR-L3 | Check claim structure: numbering is sequential, dependent claims reference existing earlier claims, and each claim ends with a period. | M |
| FR-L4 | Check abstract length against a configurable limit (default 150 words). | S |
| FR-L5 | Return findings as a list with severity (error, warning, info), rule ID, message and the location in the document. | M |
| FR-L6 | Rules are data-driven (a config file), so new rules are added without changing the engine. | S |
| FR-L7 | The linter runs deterministically with no AI call; an optional AI pass for wording issues is a later add-on. | C |

### Patent document generator (FR-G)

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-G1 | User creates a project, attaches source files, and starts a generation job. | M |
| FR-G2 | Accepted inputs: documents (.pdf, .docx, .txt, .md), images (.png, .jpg), and other reference files. | M |
| FR-G3 | Backend extracts text from documents and passes images to a vision-capable model on Near AI Cloud. | M |
| FR-G4 | Generation produces every section the linter requires, drafted from the inputs. | M |
| FR-G5 | The generator may call patent search to surface prior art and include it in the background section. | S |
| FR-G6 | Output is a .docx file that passes the linter with no errors. | M |
| FR-G7 | Generation streams progress and partial output to the UI while the job runs. | M |
| FR-G8 | Users can regenerate a single section with added instructions. | S |
| FR-G9 | Each generated document is stored with its inputs and a version number. | S |

### Uploads and storage (FR-U)

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-U1 | Files uploaded to a project are used as generation context only. Upload by drag and drop or file picker, with progress and a per-file size limit (default 25 MB). Linting and other operations take the submitted patent file, or the generated output file, identified by its file path. | M |
| FR-U2 | Files are validated by type and size, stored on local disk, and tracked in the database. | M |
| FR-U3 | Users can list, preview and delete uploaded files per project. | M |

### Browser UI (FR-UI)

| ID | Requirement | Pri |
| --- | --- | --- |
| FR-UI1 | One app with three workspaces: Search, Linter, Generator, reachable from a sidebar. | M |
| FR-UI2 | Search workspace: query box, filters, result list, detail panel. | M |
| FR-UI3 | Linter workspace: upload a .docx, show findings grouped by severity, click a finding to jump to its location in a document preview. | M |
| FR-UI4 | Generator workspace: project list, file upload area, instructions field, run button, live progress, section-by-section result view, download as .docx. | M |
| FR-UI5 | A generated document can be sent to the linter in one click. | S |
| FR-UI6 | Settings screen for backend URL and connection status; API keys are never entered or shown in the UI. | S |
| FR-UI7 | Loading, empty and error states on every screen. | M |

## Nonfunctional requirements

Inference speed and secret handling matter most; the cloud items are planned now but only designed for in v1.

| ID | Area | Requirement | Pri |
| --- | --- | --- | --- |
| NFR-1 | Cloud API key | The Near AI Cloud key lives only in backend environment variables (`.env`, git-ignored). It is never sent to the frontend, logged, or committed. | M |
| NFR-2 | Inference key | Use one shared account token with credits. Backend reads it at startup and fails fast with a clear message if missing. | M |
| NFR-3 | Inference speed | Stream tokens from the model; first progress shown in the UI within 3 seconds of starting a job. | M |
| NFR-4 | Inference speed | Generate independent sections in parallel and cache extracted text so a rerun does not repeat extraction. | S |
| NFR-5 | Search speed | Search returns within 500 ms at the 95th percentile on a corpus of 100,000 patents. | M |
| NFR-6 | Linter speed | Lint a 50-page .docx in under 2 seconds. | S |
| NFR-7 | Database | Local SQLite in v1. All access goes through SQLAlchemy models and Alembic migrations, so moving to AWS RDS (Postgres) is a connection-string change plus a migration run. Search uses SQLite FTS5 indexes sized for 100,000 patents. | M |
| NFR-8 | Cloud database | Document the RDS target: schema parity, connection pooling, and secrets via AWS Secrets Manager. Not built in v1. | C |
| NFR-9 | Cloud API | The backend must run unchanged locally and as a hosted service: config only through environment variables. | S |
| NFR-10 | Reliability | Failed or timed-out model calls retry with backoff (up to 3 attempts); a failed job reports which section failed and can be resumed. | M |
| NFR-11 | Privacy | Patent inputs are confidential. Files stay on local disk, and only the text and images needed for a job go to Near AI Cloud. Uploaded inputs are referenced by file path only, and each individual's work is kept for 30 days, then deleted. | M |
| NFR-12 | Cost control | Use low-cost DeepSeek models on Near AI Cloud, since the total budget is $20. Log token usage per job and enforce a configurable per-job token cap and a total spend limit. | S |
| NFR-13 | Portability | Runs on macOS, Windows and Linux with Python 3.11+ and Node 20+. Setup in one documented command per side. | M |
| NFR-14 | Quality | Backend: pytest with at least 80% coverage on the linter and search modules. Frontend: Vitest unit and component tests on the three workspaces. CI runs both. | S |
| NFR-15 | Maintainability | Backend exposes an OpenAPI schema; the frontend generates its API client from it, so the contract cannot drift. | M |
| NFR-16 | Usability | Every long-running action shows progress and can be cancelled. | S |

## Work split

The split is along the API line: Collaborator A owns everything behind HTTP, Collaborator B owns everything in the browser. Both can start on day one because B develops against a mock server generated from the agreed OpenAPI contract.

### Collaborator A: Python backend

| Area | Deliverables | Covers |
| --- | --- | --- |
| Project setup | FastAPI app, config from environment, SQLAlchemy + Alembic, pytest, lint/format config | NFR-1, 2, 7, 9, 13 |
| Search | Patent models, seed script, repository interface, search endpoints, MCP server wrapper | FR-S1 to S6, NFR-5 |
| Linter | .docx parser, rule engine, rule config file, `/lint` endpoint | FR-L1 to L7, NFR-6 |
| Uploads | Upload endpoints, file validation, local storage, text extraction (PDF, docx, txt) | FR-U1 to U3, FR-G2 |
| Generator | Near AI Cloud client, prompt templates per section, vision input, job runner with streaming (SSE), retry, token logging, .docx writer | FR-G1 to G9, NFR-3, 4, 10, 12 |
| Contract | OpenAPI schema kept current, mock-friendly examples, published as the source of truth | NFR-15 |

### Collaborator B: Vite + React frontend

| Area | Deliverables | Covers |
| --- | --- | --- |
| Project setup | Vite + React + TypeScript, router, state/query library, component library, Vitest setup, generated API client from OpenAPI | NFR-13, 14, 15 |
| App shell | Sidebar with three workspaces, settings screen, backend connection status, global error and loading handling | FR-UI1, UI6, UI7 |
| Search UI | Query box, filters, results list, detail panel | FR-UI2 |
| Linter UI | Upload, findings list grouped by severity, document preview with jump-to-location | FR-UI3 |
| Generator UI | Project list, drag-and-drop uploader with progress, instructions field, live streaming view, per-section regenerate, .docx download, send-to-linter | FR-UI4, UI5, FR-U1 to U3, NFR-16 |
| Mocking | Mock server (for example MSW or Prism) from the OpenAPI file so UI work is not blocked on the backend | none (enabler) |

### Shared responsibilities

- Agree the OpenAPI contract in the first two days; changes after that go through a pull request that both approve.
- Repository layout: `/backend` and `/frontend` in one repo, with a root README covering setup.
- Each side reviews the other's pull requests that touch the contract.
- A joint end-to-end test: upload sample inputs, generate, lint, and download.

## API contract

This is the proposed first draft of the REST surface; Collaborator A turns it into the OpenAPI file and both sign off on it. All paths are under `/api/v1`, bodies are JSON unless noted.

| Method and path | Purpose | Request | Response |
| --- | --- | --- | --- |
| GET `/health` | Connection check for the UI | none | status, version |
| GET `/patents/search` | Search patents | query params: `q`, filters, `page` | results, total count |
| GET `/patents/{id}` | Patent detail | none | full record, cited patents |
| POST `/lint` | Lint a .docx | multipart file | list of findings (severity, rule, message, location) |
| POST `/projects` | Create a generation project | name, description | project |
| GET `/projects` | List projects | none | projects |
| POST `/projects/{id}/files` | Upload a source file | multipart file | file record |
| GET `/projects/{id}/files` | List source files | none | file records |
| DELETE `/projects/{id}/files/{fileId}` | Remove a source file | none | empty |
| POST `/projects/{id}/generate` | Start a generation job | instructions, optional section list | job ID |
| GET `/jobs/{jobId}/events` | Stream progress and partial sections (server-sent events) | none | event stream |
| POST `/jobs/{jobId}/cancel` | Cancel a running job | none | job status |
| POST `/projects/{id}/sections/{name}/regenerate` | Regenerate one section | extra instructions | job ID |
| GET `/projects/{id}/documents/{version}` | Download the generated .docx | none | file |

Error responses use one shape: HTTP status, a machine-readable `code`, and a human-readable `message`. The MCP server exposes `search_patents` and `get_patent` with the same parameters as the two search endpoints.

## Milestones and open questions

The milestones are proposed relative to project start, assuming two people working roughly full time.

| Phase | Weeks | Collaborator A (backend) | Collaborator B (frontend) | Exit check |
| --- | --- | --- | --- | --- |
| 1. Foundations | 1 | Repo scaffold, config, DB and migrations, first OpenAPI draft | Vite app scaffold, mock server, generated client | Both sides agree the contract; `/health` shown in the UI |
| 2. Search and linter | 2 to 3 | Seed data, search API and MCP, linter engine | App shell, Search UI, Linter UI | Search and lint work end to end |
| 3. Generator | 4 to 6 | Uploads, extraction, Near AI client, job runner, SSE, .docx writer | Uploader, Generator UI, streaming view | A sample input produces a .docx that lints clean |
| 4. Hardening | 7 | Retries, token caps, performance tuning | Error states, cancel, per-section regenerate | Meets NFR-3 and NFR-5 targets |
| 5. Cloud readiness | 8 | RDS migration notes, config review | Local build and serve notes (browser tab) | Cloud plan written; browser-tab delivery confirmed |

**Open questions and decisions**

| Question | Decision | Applied in |
| --- | --- | --- |
| Does the linter target one jurisdiction's format (for example USPTO), or a generic structure? | USPTO. | FR-L2 |
| Which Near AI Cloud models are available, and do they accept image input? | Confirmed via `cloud-api.near.ai/v1/models`: `deepseek/deepseek-v4.1-flash` is ready now, accepts text+image input, 1M context, $0.30/$1.20 per M tokens in/out. Used as the default model. | NFR-12, FR-G3 |
| Is the linter's input always a .docx, or should it also accept PDF? | Also accept PDF. | FR-L1 |
| Desktop packaging: browser tab, or a wrapped app? | Browser tab. | Overview assumptions, phase 5 |
| Expected size of the real patent database? | 100,000 patents; design and test for that scale. | FR-S6, NFR-5, NFR-7 |
| Retention: how long should inputs and drafts stay on disk? | Inputs are stored by file path only; each individual's work is kept for 30 days. | NFR-11 |

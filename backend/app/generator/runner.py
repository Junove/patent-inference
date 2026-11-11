"""Job orchestration (FR-G1, FR-G4, FR-G7, FR-G9, NFR-3, NFR-4, NFR-10, NFR-12).

A job is a single asyncio task per process -- this is a local, single-user app,
so no external queue is needed. Progress is pushed onto an in-memory queue per
job and also persisted to the Job row, so the SSE endpoint can stream it live
while it runs and still report a final status after a reconnect.

shortcut: job state lives only in process memory (plus the DB row); a backend
restart loses any job that was mid-flight. Acceptable for a local dev tool;
upgrade to a persisted work queue if this ever runs as a long-lived service.
"""
import asyncio
import json
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal
from app.errors import ApiError
from app.generator import deps, extraction, prompts
from app.generator.docx_writer import next_version, write_docx
from app.linter import engine as linter_engine
from app.linter.engine import load_rules
from app.linter.parser import extract_lines
from app.models import Document, Job, Project, ProjectFile
from app.search.deps import get_patent_repository

_queues: dict[str, asyncio.Queue] = {}
_tasks: dict[str, asyncio.Task] = {}


def sections_order() -> list[str]:
    return load_rules()["sections"]


def _total_spend(db: Session) -> float:
    tokens = db.scalars(select(Job.tokens_used)).all()
    return sum(tokens) / 1000 * get_settings().near_ai_price_per_1k_tokens


def _latest_succeeded_sections(db: Session, project_id: str) -> dict:
    job = db.scalars(select(Job).where(Job.project_id == project_id, Job.status == "succeeded")
                      .order_by(Job.created_at.desc())).first()
    return json.loads(job.sections) if job else {}


def create_job(db: Session, project_id: str, instructions: str, requested: list[str]) -> Job:
    """Starts a fresh job, carrying over sections from the latest successful run that
    weren't requested this time -- this is what makes both a resume (re-request just the
    sections that failed) and a single-section regenerate (FR-G8) produce a complete document."""
    if _total_spend(db) >= get_settings().near_ai_total_budget_usd:
        raise ApiError(402, "budget_exceeded", "Near AI Cloud spending limit reached")

    carried = _latest_succeeded_sections(db, project_id)
    sections = {name: carried[name] for name in sections_order() if name in carried and name not in requested}
    for name in requested:
        sections[name] = {"status": "queued", "text": "", "error": "", "attempts": 0}

    job = Job(project_id=project_id, instructions=instructions, status="queued", sections=json.dumps(sections))
    db.add(job)
    db.commit()
    return job


def start(job_id: str) -> None:
    queue: asyncio.Queue = asyncio.Queue()
    _queues[job_id] = queue
    _tasks[job_id] = asyncio.create_task(_run(job_id, queue))


def cancel(job_id: str) -> None:
    task = _tasks.get(job_id)
    if task and not task.done():
        task.cancel()


def _final_status_payload(db: Session, job: Job) -> dict:
    """Rebuilds the same payload a live run would have pushed, for a reader that
    connects (or reconnects) after the job already finished."""
    payload = {"job_id": job.id, "status": job.status}
    if job.status == "failed":
        payload["error"] = job.error
    elif job.status == "succeeded":
        doc = db.scalars(select(Document).where(Document.job_id == job.id)).first()
        if doc:
            payload["version"] = doc.version
            findings = linter_engine.lint(extract_lines(Path(doc.path).name, Path(doc.path).read_bytes()))
            payload["lint_findings"] = [f.model_dump() for f in findings]
    return payload


async def stream_events(job_id: str) -> AsyncIterator[str]:
    queue = _queues.get(job_id)
    if queue is None:  # job finished before this reader connected (or a prior process)
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            if job:
                yield _sse("status", _final_status_payload(db, job))
        return
    while True:
        item = await queue.get()
        if item is None:
            break
        event, data = item
        yield _sse(event, data)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _prior_art(query: str) -> str:
    results, _ = get_patent_repository().search(query, page=1, page_size=3)
    return "\n".join(f"- {p.title}: {p.abstract}" for p in results)


async def _generate_section(job_id: str, queue: asyncio.Queue, name: str, context_text: str,
                             images: list[str], instructions: str, prior_art: str, sections: dict) -> None:
    settings = get_settings()
    for attempt in range(1, 4):
        with SessionLocal() as db:
            tokens_used = db.get(Job, job_id).tokens_used
        if tokens_used >= settings.near_ai_job_token_cap:
            sections[name] = {"status": "failed", "text": "", "error": "token_cap_exceeded", "attempts": attempt}
            await queue.put(("section", {"name": name, **sections[name]}))
            return

        await queue.put(("section", {"name": name, "status": "running", "attempt": attempt}))
        try:
            text, tokens = "", 0
            client = deps.get_near_ai_client()
            messages = prompts.build_messages(name, context_text, images, instructions, prior_art)
            async for chunk in client.stream(messages, max_tokens=settings.near_ai_max_tokens):
                if chunk.delta:
                    text += chunk.delta
                    await queue.put(("token", {"name": name, "delta": chunk.delta}))
                if chunk.usage:
                    tokens = chunk.usage.get("total_tokens", tokens)
            sections[name] = {"status": "done", "text": text.strip(), "error": "", "attempts": attempt}
            with SessionLocal() as db:
                job = db.get(Job, job_id)
                job.tokens_used += tokens
                db.commit()
            await queue.put(("section", {"name": name, "status": "done"}))
            return
        except asyncio.CancelledError:
            raise
        except Exception as e:
            if attempt == 3:
                sections[name] = {"status": "failed", "text": "", "error": str(e), "attempts": attempt}
                await queue.put(("section", {"name": name, "status": "failed", "error": str(e)}))
                return
            await asyncio.sleep(settings.near_ai_retry_backoff_seconds * attempt)


async def _run(job_id: str, queue: asyncio.Queue) -> None:
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        project = db.get(Project, job.project_id)
        files = db.scalars(select(ProjectFile).where(ProjectFile.project_id == job.project_id)).all()
        sections = json.loads(job.sections)
        instructions = job.instructions
        job.status = "running"
        db.commit()
    await queue.put(("status", {"job_id": job_id, "status": "running"}))

    context_text, images = extraction.build_context(files)
    prior_art = ""
    if sections.get("Background", {}).get("status") == "queued":
        prior_art = _prior_art(f"{project.name} {instructions}".strip())

    to_run = [name for name, s in sections.items() if s["status"] == "queued"]
    try:
        await asyncio.gather(*(_generate_section(job_id, queue, name, context_text, images, instructions,
                                                  prior_art, sections) for name in to_run))
    except asyncio.CancelledError:
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            job.status = "cancelled"
            job.sections = json.dumps(sections)
            db.commit()
        await queue.put(("status", {"job_id": job_id, "status": "cancelled"}))
        await queue.put(None)
        _queues.pop(job_id, None)
        _tasks.pop(job_id, None)
        return

    failed = [name for name, s in sections.items() if s["status"] == "failed"]
    # Only a complete set of sections (this run plus whatever was carried over) can become a
    # document the linter will accept (FR-G6); a deliberately partial request (e.g. drafting one
    # section before any full run exists) just leaves its results on the job for next time.
    complete = not failed and all(sections.get(name, {}).get("status") == "done" for name in sections_order())
    try:
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            job.sections = json.dumps(sections)
            if failed:
                job.status = "failed"
                job.error = f"Section(s) failed: {', '.join(failed)}"
                db.commit()
                await queue.put(("status", {"job_id": job_id, "status": "failed", "error": job.error}))
            elif complete:
                ordered = {name: sections[name]["text"] for name in sections_order()}
                version = next_version(job.project_id)
                path = write_docx(job.project_id, version, ordered)
                findings = linter_engine.lint(extract_lines(path.name, path.read_bytes()))
                db.add(Document(project_id=job.project_id, job_id=job_id, version=version, path=str(path)))
                job.status = "succeeded"
                db.commit()
                await queue.put(("status", {"job_id": job_id, "status": "succeeded", "version": version,
                                             "lint_findings": [f.model_dump() for f in findings]}))
            else:
                job.status = "succeeded"
                db.commit()
                await queue.put(("status", {"job_id": job_id, "status": "succeeded"}))
    except Exception as e:  # a job must always reach a terminal state and close its SSE stream
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            job.status = "failed"
            job.error = str(e)
            db.commit()
        await queue.put(("status", {"job_id": job_id, "status": "failed", "error": str(e)}))
    await queue.put(None)
    _queues.pop(job_id, None)
    _tasks.pop(job_id, None)

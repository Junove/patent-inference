import asyncio
import json

from app.config import get_settings
from app.generator import deps
from app.generator.client import ChatChunk, NearAIClient
from app.linter import engine as linter_engine
from app.linter.parser import extract_lines

SECTION_SAMPLES = {
    "Title": "A Widget With Improved Grip",
    "Abstract": "A widget with a textured grip surface that improves handling in wet conditions for users.",
    "Background": "Existing widgets lack adequate grip, causing slippage during use in humid environments.",
    "Summary": "The invention adds a textured grip region bonded to a widget body to improve handling.",
    "Drawings Description": "FIG. 1 is a perspective view of the widget showing the grip region.",
    "Detailed Description": "The widget includes a body and a textured grip region bonded to the body surface.",
    "Claims": "1. A widget comprising a body and a grip region bonded to the body.\n"
              "2. The widget of claim 1, wherein the grip region is textured.",
}


def _prompt_text(messages: list[dict]) -> str:
    return messages[-1]["content"][0]["text"]


class FakeNearAIClient(NearAIClient):
    """Stands in for Near AI Cloud: returns a canned answer per section, streamed
    word by word, after `fail_times` simulated transient failures."""

    def __init__(self, fail_times: int = 0, delay: float = 0.0):
        self.fail_times = fail_times
        self.delay = delay
        self.calls = 0

    async def stream(self, messages, *, max_tokens):
        self.calls += 1
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.fail_times > 0:
            self.fail_times -= 1
            raise RuntimeError("simulated Near AI Cloud failure")
        prompt = _prompt_text(messages)
        section = next(name for name in SECTION_SAMPLES if f'"{name}"' in prompt)
        for word in SECTION_SAMPLES[section].split(" "):
            yield ChatChunk(delta=word + " ")
        yield ChatChunk(delta="", usage={"total_tokens": 50})


def _project(client) -> str:
    return client.post("/api/v1/projects", json={"name": "Widget"}).json()["id"]


def _consume_events(client, job_id: str) -> list[tuple[str, dict]]:
    events = []
    with client.stream("GET", f"/api/v1/jobs/{job_id}/events") as r:
        event = None
        for line in r.iter_lines():
            if line.startswith("event: "):
                event = line.removeprefix("event: ")
            elif line.startswith("data: "):
                events.append((event, json.loads(line.removeprefix("data: "))))
    return events


def test_generate_produces_lint_clean_docx(client, monkeypatch):
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: FakeNearAIClient())
    project_id = _project(client)
    client.post(f"/api/v1/projects/{project_id}/files",
                files={"file": ("spec.txt", b"A widget with a textured grip.", "text/plain")})

    job_id = client.post(f"/api/v1/projects/{project_id}/generate", json={}).json()["job_id"]
    events = _consume_events(client, job_id)

    final = next(d for e, d in events if e == "status" and d["status"] in ("succeeded", "failed"))
    assert final["status"] == "succeeded" and final["version"] == 1
    assert final["lint_findings"] == []

    doc = client.get(f"/api/v1/projects/{project_id}/documents/1")
    assert doc.status_code == 200
    findings = linter_engine.lint(extract_lines("v1.docx", doc.content))
    assert findings == []


def test_retry_recovers_from_transient_failure(client, monkeypatch):
    fake = FakeNearAIClient(fail_times=2)
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: fake)
    monkeypatch.setattr(get_settings(), "near_ai_retry_backoff_seconds", 0.0)
    project_id = _project(client)
    job_id = client.post(f"/api/v1/projects/{project_id}/generate", json={"sections": ["Title"]}).json()["job_id"]
    events = _consume_events(client, job_id)
    final = next(d for e, d in events if e == "status" and d["status"] in ("succeeded", "failed"))
    assert final["status"] == "succeeded"


def test_retry_exhausted_fails_job_and_resume_succeeds(client, monkeypatch):
    fake = FakeNearAIClient(fail_times=5)
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: fake)
    monkeypatch.setattr(get_settings(), "near_ai_retry_backoff_seconds", 0.0)
    project_id = _project(client)

    job_id = client.post(f"/api/v1/projects/{project_id}/generate",
                          json={"sections": ["Title", "Abstract"]}).json()["job_id"]
    events = _consume_events(client, job_id)
    final = next(d for e, d in events if e == "status" and d["status"] in ("succeeded", "failed"))
    assert final["status"] == "failed"

    # resume: regenerate just the still-failing sections now that Near AI "recovers"
    fake.fail_times = 0
    job_id2 = client.post(f"/api/v1/projects/{project_id}/generate",
                           json={"sections": ["Title", "Abstract"]}).json()["job_id"]
    events2 = _consume_events(client, job_id2)
    final2 = next(d for e, d in events2 if e == "status" and d["status"] in ("succeeded", "failed"))
    assert final2["status"] == "succeeded"


def test_budget_exceeded_rejects_new_job(client, monkeypatch):
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: FakeNearAIClient())
    monkeypatch.setattr(get_settings(), "near_ai_total_budget_usd", 0.0)
    project_id = _project(client)
    r = client.post(f"/api/v1/projects/{project_id}/generate", json={})
    assert r.status_code == 402 and r.json()["code"] == "budget_exceeded"


def test_token_cap_fails_sections_without_calling_model(client, monkeypatch):
    fake = FakeNearAIClient()
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: fake)
    monkeypatch.setattr(get_settings(), "near_ai_job_token_cap", 0)
    project_id = _project(client)
    job_id = client.post(f"/api/v1/projects/{project_id}/generate", json={"sections": ["Title"]}).json()["job_id"]
    events = _consume_events(client, job_id)
    final = next(d for e, d in events if e == "status" and d["status"] in ("succeeded", "failed"))
    assert final["status"] == "failed"
    assert fake.calls == 0


def test_cancel_job(client, monkeypatch):
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: FakeNearAIClient(delay=0.3))
    project_id = _project(client)
    job_id = client.post(f"/api/v1/projects/{project_id}/generate", json={"sections": ["Title"]}).json()["job_id"]
    cancelled = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert cancelled.status_code == 200
    events = _consume_events(client, job_id)
    assert events[-1] == ("status", {"job_id": job_id, "status": "cancelled"})


def test_regenerate_section_merges_into_new_version(client, monkeypatch):
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: FakeNearAIClient())
    project_id = _project(client)
    first = client.post(f"/api/v1/projects/{project_id}/generate", json={}).json()["job_id"]
    _consume_events(client, first)

    second = client.post(f"/api/v1/projects/{project_id}/sections/Claims/regenerate", json={}).json()["job_id"]
    events = _consume_events(client, second)
    final = next(d for e, d in events if e == "status" and d["status"] in ("succeeded", "failed"))
    assert final["status"] == "succeeded" and final["version"] == 2

    assert client.get(f"/api/v1/projects/{project_id}/documents/1").status_code == 200
    assert client.get(f"/api/v1/projects/{project_id}/documents/2").status_code == 200


def test_invalid_section_name_rejected(client, monkeypatch):
    monkeypatch.setattr(deps, "get_near_ai_client", lambda: FakeNearAIClient())
    project_id = _project(client)
    r = client.post(f"/api/v1/projects/{project_id}/generate", json={"sections": ["Nope"]})
    assert r.status_code == 400 and r.json()["code"] == "invalid_section"

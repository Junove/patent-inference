import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.export_openapi import CONTRACT, render
from app.main import app


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_projects_roundtrip(client):
    created = client.post("/api/v1/projects", json={"name": "Widget"})
    assert created.status_code == 201
    assert created.json()["name"] == "Widget"
    assert created.json()["id"] in [p["id"] for p in client.get("/api/v1/projects").json()]


def test_error_shape(client):
    bad = client.post("/api/v1/projects", json={})
    assert bad.status_code == 422 and set(bad.json()) == {"code", "message"}
    missing_project = client.post("/api/v1/projects/p1/generate", json={})
    assert missing_project.status_code == 404 and missing_project.json()["code"] == "not_found"
    assert client.get("/api/v1/nope").json()["code"] == "http_error"


def test_fails_fast_without_api_key(monkeypatch):
    monkeypatch.setattr(get_settings(), "near_ai_api_key", "")
    with pytest.raises(RuntimeError, match="NEAR_AI_API_KEY"):
        with TestClient(app):
            pass


def test_committed_contract_is_current():
    assert CONTRACT.read_text() == render(), "run: python -m app.export_openapi"

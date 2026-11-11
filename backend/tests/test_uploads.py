from datetime import datetime, timedelta, timezone

from app import uploads
from app.config import get_settings
from app.db import SessionLocal


def _project(client) -> str:
    return client.post("/api/v1/projects", json={"name": "Widget"}).json()["id"]


def test_upload_list_delete_roundtrip(client):
    project_id = _project(client)
    r = client.post(f"/api/v1/projects/{project_id}/files",
                     files={"file": ("spec.txt", b"hello world", "text/plain")})
    assert r.status_code == 201
    file = r.json()
    assert file["filename"] == "spec.txt" and file["size"] == 11

    listed = client.get(f"/api/v1/projects/{project_id}/files").json()
    assert [f["id"] for f in listed] == [file["id"]]

    assert client.delete(f"/api/v1/projects/{project_id}/files/{file['id']}").status_code == 204
    assert client.get(f"/api/v1/projects/{project_id}/files").json() == []


def test_upload_rejects_oversized_file(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "upload_max_bytes", 4)
    project_id = _project(client)
    r = client.post(f"/api/v1/projects/{project_id}/files",
                     files={"file": ("big.txt", b"too big", "text/plain")})
    assert r.status_code == 413 and r.json()["code"] == "file_too_large"


def test_upload_requires_existing_project(client):
    r = client.post("/api/v1/projects/nope/files", files={"file": ("a.txt", b"x", "text/plain")})
    assert r.status_code == 404


def test_delete_requires_existing_file(client):
    project_id = _project(client)
    r = client.delete(f"/api/v1/projects/{project_id}/files/nope")
    assert r.status_code == 404


def test_purge_expired_removes_old_files(client):
    project_id = _project(client)
    with SessionLocal() as db:
        record = uploads.save(project_id, "old.txt", "text/plain", b"stale", db)
        record.created_at = datetime.now(timezone.utc) - timedelta(days=31)
        db.add(record)
        db.commit()
        file_id = record.id

        uploads.purge_expired(db)
        assert db.get(record.__class__, file_id) is None
    assert client.get(f"/api/v1/projects/{project_id}/files").json() == []

import os
import tempfile

# must be set before the app imports its settings and engine
_tmp = tempfile.mkdtemp()
os.environ.update(NEAR_AI_API_KEY="test-key", DATABASE_URL=f"sqlite:///{_tmp}/test.db", UPLOAD_DIR=f"{_tmp}/uploads")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    command.upgrade(Config("alembic.ini"), "head")  # also proves the migration applies
    with TestClient(app) as c:  # enters lifespan
        yield c


@pytest.fixture(scope="session")
def patent_repo(client):
    """A couple of hand-picked patents (deterministic), inserted once per session."""
    from app.search.deps import get_patent_repository
    from app.search.sqlite_fts import insert_patents

    repo = get_patent_repository()
    insert_patents(repo.db, [
        dict(id="US9999001", title="Solid-state battery electrolyte",
             abstract="A sulfide electrolyte for fast lithium-ion transport.",
             claims=["1. A battery comprising a housing.", "2. The battery of claim 1, further comprising a sensor."],
             inventors=["Ada Lovelace"], assignee="Acme Corp", filing_date="2024-01-15",
             classification=["H01M"], cited_ids=[]),
        dict(id="US9999002", title="Wireless charging alignment pad",
             abstract="Magnetic alignment system for inductive charging.",
             claims=["1. A pad comprising a coil."], inventors=["Grace Hopper"], assignee="Northwind Labs",
             filing_date="2023-06-01", classification=["H02J"], cited_ids=["US9999001"]),
    ])
    return repo

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

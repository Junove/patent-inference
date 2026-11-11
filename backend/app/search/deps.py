"""Shared connection + FastAPI dependency. Swapping to a real patent source
(FR-S5) means changing only sqlite_fts.py and this file's connect() call."""
from functools import lru_cache

from app.config import get_settings
from app.search.sqlite_fts import SqlitePatentRepository, connect


def sqlite_path(url: str) -> str:
    if not url.startswith("sqlite:///"):
        raise RuntimeError("Patent search needs a sqlite:/// DATABASE_URL in v1")
    return url.removeprefix("sqlite:///")


@lru_cache
def _connection():
    return connect(sqlite_path(get_settings().database_url))


def get_patent_repository() -> SqlitePatentRepository:
    return SqlitePatentRepository(_connection())

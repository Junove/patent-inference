"""NFR-5 (search <500ms p95 at 100k patents). Not run by default: `uv run pytest -m slow`."""
import time

import pytest

from app.search.seed import add_synthetic
from app.search.sqlite_fts import SqlitePatentRepository, connect


@pytest.mark.slow
def test_search_meets_latency_target_at_100k(tmp_path):
    db_path = str(tmp_path / "perf.db")
    add_synthetic(db_path, n=100_000)
    repo = SqlitePatentRepository(connect(db_path))
    start = time.perf_counter()
    for _ in range(20):
        repo.search("battery", page=1, page_size=10)
    avg = (time.perf_counter() - start) / 20
    assert avg < 0.5, f"average search took {avg:.3f}s (budget 0.5s, NFR-5)"

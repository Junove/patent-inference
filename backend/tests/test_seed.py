from app.search.seed import add_synthetic, generate, seed
from app.search.sqlite_fts import connect, count


def test_generate_is_deterministic_and_well_formed():
    a, b = generate(5, seed=1), generate(5, seed=1)
    assert a == b
    assert len({p["id"] for p in a}) == 5
    for p in a:
        assert p["claims"][0].startswith("1. ")


def test_seed_is_idempotent_and_add_synthetic_appends(tmp_path):
    db_path = str(tmp_path / "s.db")
    seed(db_path, dev_count=10)
    assert count(connect(db_path)) == 10
    seed(db_path, dev_count=10)  # table already populated: no-op
    assert count(connect(db_path)) == 10
    add_synthetic(db_path, n=5, seed_value=2)
    assert count(connect(db_path)) == 15


def test_seed_reset_replaces_corpus(tmp_path):
    db_path = str(tmp_path / "r.db")
    seed(db_path, dev_count=10)
    seed(db_path, dev_count=3, reset=True)
    assert count(connect(db_path)) == 3

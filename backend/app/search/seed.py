"""Reproducible synthetic patent corpus (FR-S6): a small dev-sized call for
everyday use, and a `generate(n, ...)` any script can call for scale testing."""
import random

from app.search.sqlite_fts import connect, count, insert_patents

AREAS = [
    ("battery", ["lithium-ion", "solid-state", "sodium-ion"], ["electrolyte", "anode", "cathode", "separator"]),
    ("wireless charging", ["inductive", "magnetic resonance", "resonant"], ["charging pad", "coil array", "alignment system"]),
    ("neural networks", ["transformer", "convolutional", "recurrent"], ["pruning method", "quantization scheme", "attention mechanism"]),
    ("trusted execution", ["hardware", "enclave-based", "remote-attested"], ["inference pipeline", "key management", "TEE runtime"]),
    ("gene editing", ["CRISPR", "base-editing", "lipid nanoparticle"], ["delivery vector", "guide RNA design", "off-target screen"]),
    ("solar cells", ["perovskite", "tandem", "thin-film"], ["photovoltaic cell", "encapsulation layer", "tracking mount"]),
    ("autonomous vehicles", ["lidar-based", "camera-only", "sensor-fusion"], ["obstacle detection", "path planning", "collision avoidance"]),
]
ASSIGNEES = ["Acme Corp", "Northwind Labs", "Fabrikam Inc", "Globex Research", "Initech Systems", "Umbrella Technologies"]
FIRST = ["Alex", "Priya", "Jordan", "Wei", "Sam", "Nina", "Omar", "Ivy"]
LAST = ["Chen", "Patel", "Garcia", "Kim", "Johnson", "Novak", "Silva", "Brooks"]
CLASS_CODES = ["H01M", "H02J", "G06N", "G06F", "C12N", "H01L", "B60W"]


def generate(n: int, *, seed: int = 42, start: int = 1) -> list[dict]:
    """n fake-but-structurally-real patents, deterministic for a given (seed, start)."""
    rnd = random.Random(seed)
    patents = []
    for i in range(n):
        num = start + i
        area, adjs, nouns = rnd.choice(AREAS)
        adj, noun = rnd.choice(adjs), rnd.choice(nouns)
        n_claims = rnd.randint(3, 8)
        claims = [
            f"1. A {noun} comprising {rnd.choice(['a housing', 'a control unit', 'a sensor array', 'a processing module'])}."
            if j == 1 else
            f"{j}. The {noun} of claim {rnd.randint(1, j - 1)}, further comprising "
            f"{rnd.choice(['a feedback loop', 'a calibration step', 'a safety interlock'])}."
            for j in range(1, n_claims + 1)
        ]
        patents.append(dict(
            id=f"US{10000000 + num}",
            title=f"{adj.capitalize()} {noun} for {area}",
            abstract=f"A {adj} {noun} that improves "
                     f"{rnd.choice(['efficiency', 'reliability', 'throughput', 'safety'])} in {area} applications.",
            claims=claims,
            inventors=[f"{rnd.choice(FIRST)} {rnd.choice(LAST)}" for _ in range(rnd.randint(1, 3))],
            assignee=rnd.choice(ASSIGNEES),
            filing_date=f"20{rnd.randint(10, 25):02d}-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}",
            classification=[rnd.choice(CLASS_CODES)],
            cited_ids=[f"US{10000000 + rnd.randint(start, num - 1)}"] if num > start else [],
        ))
    return patents


def seed(db_path: str, dev_count: int = 300, reset: bool = False) -> None:
    db = connect(db_path)
    if reset:
        db.execute("DELETE FROM patents_fts")
        db.commit()
    if count(db) == 0:
        insert_patents(db, generate(dev_count))


def add_synthetic(db_path: str, n: int = 100_000, seed_value: int = 7) -> None:
    """Appends n more records for perf testing (NFR-5); does not touch existing rows."""
    db = connect(db_path)
    insert_patents(db, generate(n, seed=seed_value, start=count(db) + 1))


if __name__ == "__main__":
    import argparse

    from app.config import get_settings
    from app.search.deps import sqlite_path

    p = argparse.ArgumentParser(description="Seed the patent search database")
    p.add_argument("--reset", action="store_true", help="wipe existing patents first")
    p.add_argument("--scale", type=int, metavar="N", help="also add N synthetic patents for perf testing")
    args = p.parse_args()

    path = sqlite_path(get_settings().database_url)
    seed(path, reset=args.reset)
    if args.scale:
        add_synthetic(path, n=args.scale)
    print(f"{count(connect(path))} patents in {path}")

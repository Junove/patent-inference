"""v1 PatentRepository: seeded SQLite FTS5 (FR-S5). Swap for a real patent
source later without touching the API layer -- only this module changes."""
import json
import sqlite3

from app.schemas import PatentDetail, PatentSummary

_COLUMNS = ["id", "title", "abstract", "claims", "inventors", "assignee", "filing_date",
            "classification", "claims_json", "inventors_json", "classification_json", "cited_ids"]


def _fts_quote(query: str) -> str:
    # quote each term so user input can't inject FTS5 syntax
    return " ".join('"%s"' % t.replace('"', "") for t in query.split())


def connect(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path, check_same_thread=False)
    db.execute(f"CREATE VIRTUAL TABLE IF NOT EXISTS patents_fts USING fts5({', '.join(_COLUMNS[:8])}, "
               "claims_json UNINDEXED, inventors_json UNINDEXED, classification_json UNINDEXED, cited_ids UNINDEXED, "
               "tokenize='porter unicode61')")
    return db


def insert_patents(db: sqlite3.Connection, patents: list[dict]) -> None:
    """Each dict: id, title, abstract, claims, inventors, assignee, filing_date,
    classification (list[str]), cited_ids (list[str])."""
    db.executemany(
        f"INSERT INTO patents_fts ({', '.join(_COLUMNS)}) VALUES ({', '.join('?' * len(_COLUMNS))})",
        [(p["id"], p["title"], p["abstract"], " ".join(p["claims"]), " ".join(p["inventors"]), p["assignee"],
          p["filing_date"], " ".join(p["classification"]), json.dumps(p["claims"]), json.dumps(p["inventors"]),
          json.dumps(p["classification"]), json.dumps(p.get("cited_ids", []))) for p in patents],
    )
    db.commit()


def count(db: sqlite3.Connection) -> int:
    return db.execute("SELECT count(*) FROM patents_fts").fetchone()[0]


class SqlitePatentRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def _where(self, query, date_from, date_to, assignee, inventor, classification):
        clauses, params = [], []
        if query:
            clauses.append("patents_fts MATCH ?")
            params.append(_fts_quote(query))
        if date_from:
            clauses.append("filing_date >= ?"); params.append(date_from)
        if date_to:
            clauses.append("filing_date <= ?"); params.append(date_to)
        if assignee:
            clauses.append("assignee = ?"); params.append(assignee)
        if inventor:
            clauses.append("inventors LIKE ?"); params.append(f"%{inventor}%")
        if classification:
            clauses.append("classification LIKE ?"); params.append(f"%{classification}%")
        return (" WHERE " + " AND ".join(clauses)) if clauses else "", params

    def search(self, query, *, page=1, page_size=10, date_from=None, date_to=None, assignee=None,
               inventor=None, classification=None):
        where, params = self._where(query, date_from, date_to, assignee, inventor, classification)
        total = self.db.execute(f"SELECT count(*) FROM patents_fts{where}", params).fetchone()[0]
        order = "rank" if query else "filing_date DESC"
        rows = self.db.execute(
            f"SELECT id, title, abstract, assignee, filing_date FROM patents_fts{where} ORDER BY {order} LIMIT ? OFFSET ?",
            [*params, page_size, (page - 1) * page_size],
        )
        results = [PatentSummary(id=r[0], title=r[1], abstract=r[2], assignee=r[3], filing_date=r[4]) for r in rows]
        return results, total

    def get(self, patent_id: str) -> PatentDetail | None:
        row = self.db.execute(
            "SELECT id, title, abstract, assignee, filing_date, claims_json, inventors_json, classification_json, "
            "cited_ids FROM patents_fts WHERE id = ?", (patent_id,),
        ).fetchone()
        if not row:
            return None
        cited_ids = json.loads(row[8]) if row[8] else []
        cited = []
        if cited_ids:
            placeholders = ",".join("?" * len(cited_ids))
            cited_rows = self.db.execute(
                f"SELECT id, title, abstract, assignee, filing_date FROM patents_fts WHERE id IN ({placeholders})",
                cited_ids,
            )
            cited = [PatentSummary(id=r[0], title=r[1], abstract=r[2], assignee=r[3], filing_date=r[4]) for r in cited_rows]
        return PatentDetail(
            id=row[0], title=row[1], abstract=row[2], assignee=row[3], filing_date=row[4],
            claims=json.loads(row[5]), inventors=json.loads(row[6]), classification=json.loads(row[7]),
            cited_patents=cited,
        )

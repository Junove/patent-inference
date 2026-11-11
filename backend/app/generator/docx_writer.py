"""Writes generated sections to a .docx that the linter can parse (FR-G6):
one heading paragraph per section, matching app/linter/rules.yaml exactly."""
import re
from pathlib import Path

from docx import Document as DocxDocument
from sqlalchemy import func, select

from app.config import get_settings
from app.db import SessionLocal
from app.models import Document as DocumentRow

_CLAIM_LEAD = re.compile(r"^\d+\.\s*")


def _renumber_claims(text: str) -> list[str]:
    """Safety net: fixes claim numbering drift from the model. Doesn't fix a
    missing period or a forward reference -- those come from the prompt."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    out = []
    for i, line in enumerate(lines, start=1):
        body = _CLAIM_LEAD.sub("", line)
        if not body.endswith("."):
            body += "."
        out.append(f"{i}. {body}")
    return out


def next_version(project_id: str) -> int:
    with SessionLocal() as db:
        current = db.scalar(select(func.max(DocumentRow.version)).where(DocumentRow.project_id == project_id))
    return (current or 0) + 1


def write_docx(project_id: str, version: int, sections: dict[str, str]) -> Path:
    folder = Path(get_settings().upload_dir) / project_id / "documents"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"v{version}.docx"

    doc = DocxDocument()
    for name, text in sections.items():
        doc.add_paragraph(name)
        if name == "Claims":
            for line in _renumber_claims(text):
                doc.add_paragraph(line)
        else:
            for para in (text or "(not generated)").split("\n"):
                if para.strip():
                    doc.add_paragraph(para.strip())
    doc.save(path)
    return path

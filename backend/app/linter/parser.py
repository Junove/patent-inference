"""Extracts a flat list of non-empty text lines from a document (FR-L1).
Structure (headings, claim numbering) survives as plain text lines; the rule
engine does the actual structural checks."""
import io
import xml.etree.ElementTree as ET

from docx import Document
from pypdf import PdfReader


def extract_lines(filename: str, data: bytes) -> list[str]:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "docx":
        return [p.text.strip() for p in Document(io.BytesIO(data)).paragraphs if p.text.strip()]
    if ext == "pdf":
        text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
        return [ln.strip() for ln in text.splitlines() if ln.strip()]
    if ext == "xml":
        root = ET.fromstring(data)
        return [el.text.strip() for el in root.iter() if el.text and el.text.strip()]
    # plain text, markdown, or unknown extension: decode and split
    return [ln.strip() for ln in data.decode("utf-8", errors="replace").splitlines() if ln.strip()]

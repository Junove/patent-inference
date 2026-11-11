"""Generates two demo patent .docx files and lints them with the real
engine so the presentation can quote exact, verified findings."""
import sys
from pathlib import Path

from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.linter.engine import lint  # noqa: E402

OUT = Path(__file__).parent


def write_docx(path: Path, paragraphs: list[str]) -> None:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    doc.save(path)


ACCURATE = [
    "Title",
    "Self-Calibrating Prior-Art Retrieval System for Patent Drafting",
    "Abstract",
    "A system retrieves prior art for a draft patent application by extracting key "
    "terms from uploaded source documents, querying an indexed corpus of patent "
    "records, and ranking results by semantic similarity to the draft's claims. "
    "The system presents ranked candidates to the user for inclusion in the "
    "background section before generation completes.",
    "Background",
    "Patent drafters manually search separate databases to find prior art, which is "
    "slow and often incomplete because keyword search misses semantically related "
    "work described with different terminology.",
    "Summary",
    "The system automatically surfaces candidate prior art during drafting by "
    "combining keyword search with embedding-based ranking, reducing manual search "
    "time and improving background section completeness.",
    "Drawings Description",
    "FIG. 1 shows the retrieval pipeline from document upload to ranked results. "
    "FIG. 2 shows the ranking model architecture.",
    "Detailed Description",
    "The system comprises an extraction module, a search index, and a ranking "
    "module. The extraction module parses uploaded documents into candidate claim "
    "terms. The search index stores patent records with full-text and metadata "
    "fields. The ranking module scores each candidate record against the extracted "
    "terms and returns the top-ranked subset to the drafting interface.",
    "Claims",
    "1. A method comprising extracting terms from a draft document, querying an "
    "indexed patent corpus with the extracted terms, and ranking returned records "
    "by similarity to the terms.",
    "2. The method of claim 1, wherein the ranking is performed by a trained "
    "embedding model.",
    "3. The method of claim 2, wherein ranked records are presented to a user "
    "before document generation completes.",
]

INACCURATE = [
    "Title",
    "A Widget System for Doing Various Unspecified Things",
    "Summary",
    "The system does several things related to widgets and is summarized here "
    "ahead of the background section, which is not where this section belongs.",
    "Background",
    "Widgets have long been difficult to manage, for reasons that are numerous "
    "and not fully enumerated in this filing.",
    "Abstract",
    "This abstract is intentionally long so that it exceeds the configured word "
    "limit for demonstration purposes, which matters because real abstracts are "
    "capped and reviewers reject applications that run past the limit, and this "
    "one keeps going well past a reasonable length by repeating similar filler "
    "phrases about widgets, systems, methods, and apparatuses in order to pad "
    "the word count past one hundred fifty words, continuing to restate the same "
    "point about widget systems and widget methods and widget apparatuses several "
    "more times so that the total word count clears the threshold comfortably and "
    "demonstrates the abstract-length warning rule in the linter engine for this "
    "presentation example document used at the hackathon demo session today, and "
    "then restating once again that the widget system, the widget method, and the "
    "widget apparatus are all described herein at unnecessary length purely to "
    "push this abstract well past the one hundred fifty word limit configured in "
    "the rules file so the warning reliably fires during the live demonstration.",
    "Detailed Description",
    "The widget system operates by receiving a widget, processing the widget, and "
    "producing a processed widget as output.",
    "Claims",
    "1. A system comprising a widget-receiving module and a widget-processing "
    "module",
    "3. The system of claim 1, wherein the widget-processing module further "
    "comprises a sub-module.",
    "4. The system of claim 3, wherein the sub-module references claim 9.",
]

write_docx(OUT / "accurate_patent.docx", ACCURATE)
write_docx(OUT / "inaccurate_patent.docx", INACCURATE)

for name, paras in [("accurate_patent.docx", ACCURATE), ("inaccurate_patent.docx", INACCURATE)]:
    lines = [p.strip() for p in paras if p.strip()]
    findings = lint(lines)
    print(f"\n=== {name}: {len(findings)} finding(s) ===")
    for f in findings:
        print(f" [{f.severity}] {f.rule}: {f.message}")

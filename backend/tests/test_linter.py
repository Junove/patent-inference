import io

from docx import Document

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
SECTIONS = ["Title", "Abstract", "Background", "Summary", "Drawings Description", "Detailed Description", "Claims"]


def _make_docx(skip=None, claims=None, abstract=None):
    body = {
        "Title": ["A Widget"],
        "Abstract": [abstract or "This invention is a widget that does things."],
        "Background": ["Prior widgets were slow."],
        "Summary": ["This widget is fast."],
        "Drawings Description": ["Figure 1 shows the widget."],
        "Detailed Description": ["The widget has a housing and a sensor."],
        "Claims": claims or ["1. A widget comprising a housing.", "2. The widget of claim 1, further comprising a sensor."],
    }
    doc = Document()
    for s in SECTIONS:
        if s == skip:
            continue
        doc.add_paragraph(s)
        for line in body[s]:
            doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _lint(client, data: bytes, filename="patent.docx", mime=DOCX_MIME):
    return client.post("/api/v1/lint", files={"file": (filename, data, mime)}).json()


def test_clean_document_has_no_errors(client):
    errors = [f for f in _lint(client, _make_docx()) if f["severity"] == "error"]
    assert errors == []


def test_missing_section(client):
    findings = _lint(client, _make_docx(skip="Background"))
    assert any(f["rule"] == "missing-section" and "Background" in f["message"] for f in findings)


def test_claim_numbering_and_period(client):
    bad_claims = ["1. A widget comprising a housing", "3. The widget of claim 1, further comprising a sensor."]
    rules = {f["rule"] for f in _lint(client, _make_docx(claims=bad_claims))}
    assert "claim-numbering" in rules
    assert "claim-period" in rules


def test_invalid_claim_reference(client):
    bad_claims = ["1. A widget comprising a housing.", "2. The widget of claim 2, further comprising a sensor."]
    rules = {f["rule"] for f in _lint(client, _make_docx(claims=bad_claims))}
    assert "invalid-claim-reference" in rules


def test_abstract_too_long(client):
    long_abstract = " ".join(["word"] * 200)
    rules = {f["rule"] for f in _lint(client, _make_docx(abstract=long_abstract))}
    assert "abstract-length" in rules


def test_unreadable_file(client):
    findings = _lint(client, b"not a docx")
    assert findings[0]["rule"] == "unreadable"


def test_plain_text_input(client):
    text = "\n".join(["Title", "A Widget", "Abstract", "Short.", "Background", "Old.", "Summary", "New.",
                       "Drawings Description", "Fig1.", "Detailed Description", "Detail.", "Claims", "1. A widget."])
    findings = _lint(client, text.encode(), filename="patent.txt", mime="text/plain")
    assert [f for f in findings if f["severity"] == "error"] == []

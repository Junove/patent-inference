import io

from docx import Document
from pypdf import PdfWriter

from app.linter.parser import extract_lines


def test_extract_lines_docx():
    doc = Document()
    doc.add_paragraph("Title")
    buf = io.BytesIO()
    doc.save(buf)
    assert extract_lines("x.docx", buf.getvalue()) == ["Title"]


def test_extract_lines_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)  # no text; just proves the pdf branch runs
    buf = io.BytesIO()
    writer.write(buf)
    assert extract_lines("x.pdf", buf.getvalue()) == []


def test_extract_lines_xml():
    xml = b"<doc><title>A Widget</title><claims>1. A widget.</claims></doc>"
    assert extract_lines("x.xml", xml) == ["A Widget", "1. A widget."]


def test_extract_lines_plain_text():
    assert extract_lines("x.txt", b"Title\nA Widget\n\n") == ["Title", "A Widget"]

"""Builds the generation context from a project's uploaded files (FR-G3).
Documents are turned into text; images are passed through as data URLs for
the vision-capable model. Extracted text is cached by (path, mtime) so a
rerun doesn't repeat it (NFR-4)."""
import base64
import mimetypes
from pathlib import Path

from app.linter.parser import extract_lines
from app.models import ProjectFile

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
_text_cache: dict[tuple[str, float], str] = {}


def build_context(files: list[ProjectFile]) -> tuple[str, list[str]]:
    texts: list[str] = []
    images: list[str] = []
    for f in files:
        path = Path(f.path)
        if not path.exists():
            continue
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            images.append(f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}")
            continue
        key = (f.path, path.stat().st_mtime)
        if key not in _text_cache:
            _text_cache[key] = "\n".join(extract_lines(f.filename, path.read_bytes()))
        texts.append(f"--- {f.filename} ---\n{_text_cache[key]}")
    return "\n\n".join(texts), images

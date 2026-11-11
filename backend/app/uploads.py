"""Local disk storage for project files (FR-U1-U3). Inputs are referenced by file
path only (NFR-11); nothing but the path and metadata is ever in the database."""
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ProjectFile


def save(project_id: str, filename: str, content_type: str, data: bytes, db: Session) -> ProjectFile:
    folder = Path(get_settings().upload_dir) / project_id / str(uuid.uuid4())
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_bytes(data)
    record = ProjectFile(id=folder.name, project_id=project_id, filename=filename,
                          path=str(path), content_type=content_type or "", size=len(data))
    db.add(record)
    db.commit()
    return record


def delete(record: ProjectFile, db: Session) -> None:
    shutil.rmtree(Path(record.path).parent, ignore_errors=True)
    db.delete(record)
    db.commit()


def purge_expired(db: Session) -> None:
    """Delete uploads past the retention window, on disk and in the database (NFR-11)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=get_settings().upload_retention_days)
    for record in db.scalars(select(ProjectFile).where(ProjectFile.created_at < cutoff)).all():
        delete(record, db)

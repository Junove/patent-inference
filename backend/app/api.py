from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas, uploads
from app.config import get_settings
from app.db import get_db
from app.errors import ApiError
from app.generator import runner
from app.linter import engine as linter_engine
from app.linter.parser import extract_lines
from app.models import Document, Job, Project, ProjectFile
from app.search.deps import get_patent_repository
from app.search.repository import PatentRepository

VERSION = "0.1.0"
router = APIRouter(prefix="/api/v1", responses={"default": {"model": schemas.Error}})


def _get_project(project_id: str, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise ApiError(404, "not_found", f"No project {project_id}")
    return project


def _valid_sections(names: list[str] | None) -> list[str]:
    order = runner.sections_order()
    if names is None:
        return order
    unknown = [n for n in names if n not in order]
    if unknown:
        raise ApiError(400, "invalid_section", f"Unknown section(s): {', '.join(unknown)}")
    return [n for n in order if n in names]


@router.get("/health", response_model=schemas.Health)
def health():
    return {"status": "ok", "version": VERSION}


@router.post("/projects", response_model=schemas.ProjectOut, status_code=201)
def create_project(body: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**body.model_dump())
    db.add(project)
    db.commit()
    return project


@router.get("/projects", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.scalars(select(Project).order_by(Project.created_at)).all()


@router.get("/patents/search", response_model=schemas.SearchResults)
def search_patents(q: str = "", page: int = Query(1, ge=1), date_from: str | None = None, date_to: str | None = None,
                    assignee: str | None = None, inventor: str | None = None, classification: str | None = None,
                    repo: PatentRepository = Depends(get_patent_repository)):
    results, total = repo.search(q, page=page, date_from=date_from, date_to=date_to, assignee=assignee,
                                  inventor=inventor, classification=classification)
    return {"results": results, "total": total}


@router.get("/patents/{patent_id}", response_model=schemas.PatentDetail)
def get_patent(patent_id: str, repo: PatentRepository = Depends(get_patent_repository)):
    detail = repo.get(patent_id)
    if detail is None:
        raise ApiError(404, "not_found", f"No patent {patent_id}")
    return detail


@router.post("/lint", response_model=list[schemas.Finding])
async def lint(file: UploadFile):
    data = await file.read()
    try:
        lines = extract_lines(file.filename or "", data)
    except Exception as e:
        return [schemas.Finding(severity="error", rule="unreadable", message=f"Could not read {file.filename}: {e}")]
    return linter_engine.lint(lines)


@router.post("/projects/{project_id}/files", response_model=schemas.FileOut, status_code=201)
async def upload_file(project_id: str, file: UploadFile, db: Session = Depends(get_db)):
    _get_project(project_id, db)
    if not file.filename:
        raise ApiError(400, "invalid_file", "File must have a filename")
    data = await file.read()
    limit = get_settings().upload_max_bytes
    if len(data) > limit:
        raise ApiError(413, "file_too_large", f"{file.filename} exceeds the {limit} byte limit")
    return uploads.save(project_id, file.filename, file.content_type or "", data, db)


@router.get("/projects/{project_id}/files", response_model=list[schemas.FileOut])
def list_files(project_id: str, db: Session = Depends(get_db)):
    _get_project(project_id, db)
    return db.scalars(select(ProjectFile).where(ProjectFile.project_id == project_id)
                       .order_by(ProjectFile.created_at)).all()


@router.delete("/projects/{project_id}/files/{file_id}", status_code=204)
def delete_file(project_id: str, file_id: str, db: Session = Depends(get_db)):
    _get_project(project_id, db)
    record = db.get(ProjectFile, file_id)
    if record is None or record.project_id != project_id:
        raise ApiError(404, "not_found", f"No file {file_id}")
    uploads.delete(record, db)


@router.post("/projects/{project_id}/generate", response_model=schemas.JobId, status_code=202)
async def generate(project_id: str, body: schemas.GenerateRequest, db: Session = Depends(get_db)):
    _get_project(project_id, db)
    sections = _valid_sections(body.sections)
    job = runner.create_job(db, project_id, body.instructions, sections)
    runner.start(job.id)
    return {"job_id": job.id}


@router.get("/jobs/{job_id}/events", responses={200: {"content": {"text/event-stream": {}}, "description": "Server-sent events"}})
async def job_events(job_id: str, db: Session = Depends(get_db)):
    if db.get(Job, job_id) is None:
        raise ApiError(404, "not_found", f"No job {job_id}")
    return StreamingResponse(runner.stream_events(job_id), media_type="text/event-stream")


@router.post("/jobs/{job_id}/cancel", response_model=schemas.JobStatus)
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise ApiError(404, "not_found", f"No job {job_id}")
    if job.status in ("queued", "running"):
        runner.cancel(job_id)
        job.status = "cancelled"
        db.commit()
    return {"job_id": job.id, "status": job.status}


@router.post("/projects/{project_id}/sections/{name}/regenerate", response_model=schemas.JobId, status_code=202)
async def regenerate_section(project_id: str, name: str, body: schemas.RegenerateRequest, db: Session = Depends(get_db)):
    _get_project(project_id, db)
    sections = _valid_sections([name])
    job = runner.create_job(db, project_id, body.instructions, sections)
    runner.start(job.id)
    return {"job_id": job.id}


@router.get("/projects/{project_id}/documents/{version}", response_class=FileResponse,
            responses={200: {"content": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}}}})
def download_document(project_id: str, version: int, db: Session = Depends(get_db)):
    doc = db.scalar(select(Document).where(Document.project_id == project_id, Document.version == version))
    if doc is None:
        raise ApiError(404, "not_found", f"No document version {version} for project {project_id}")
    return FileResponse(doc.path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                         filename=f"{project_id}-v{version}.docx")

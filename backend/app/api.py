from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from app.db import get_db
from app.errors import ApiError
from app.linter import engine as linter_engine
from app.linter.parser import extract_lines
from app.models import Project
from app.search.deps import get_patent_repository
from app.search.repository import PatentRepository

VERSION = "0.1.0"
router = APIRouter(prefix="/api/v1", responses={"default": {"model": schemas.Error}})


def _todo(feature: str):
    raise ApiError(501, "not_implemented", f"{feature} is not implemented yet")


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


# --- contract stubs: implemented in later phases ---
@router.post("/projects/{project_id}/files", response_model=schemas.FileOut, status_code=201)
def upload_file(project_id: str, file: UploadFile):
    _todo("File upload")


@router.get("/projects/{project_id}/files", response_model=list[schemas.FileOut])
def list_files(project_id: str):
    _todo("File listing")


@router.delete("/projects/{project_id}/files/{file_id}", status_code=204)
def delete_file(project_id: str, file_id: str):
    _todo("File deletion")


@router.post("/projects/{project_id}/generate", response_model=schemas.JobId, status_code=202)
def generate(project_id: str, body: schemas.GenerateRequest):
    _todo("Generation")


@router.get("/jobs/{job_id}/events", responses={200: {"content": {"text/event-stream": {}}, "description": "Server-sent events"}})
def job_events(job_id: str):
    _todo("Job events")


@router.post("/jobs/{job_id}/cancel", response_model=schemas.JobStatus)
def cancel_job(job_id: str):
    _todo("Job cancellation")


@router.post("/projects/{project_id}/sections/{name}/regenerate", response_model=schemas.JobId, status_code=202)
def regenerate_section(project_id: str, name: str, body: schemas.RegenerateRequest):
    _todo("Section regeneration")


@router.get("/projects/{project_id}/documents/{version}", response_class=FileResponse,
            responses={200: {"content": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}}}})
def download_document(project_id: str, version: int):
    _todo("Document download")

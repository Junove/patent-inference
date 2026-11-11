from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Health(BaseModel):
    status: Literal["ok"]
    version: str


class Error(BaseModel):
    code: str
    message: str


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectOut(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    content_type: str
    size: int
    created_at: datetime


class GenerateRequest(BaseModel):
    instructions: str = ""
    sections: list[str] | None = None


class RegenerateRequest(BaseModel):
    instructions: str = ""


class JobId(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed", "cancelled"]


class Finding(BaseModel):
    severity: Literal["error", "warning", "info"]
    rule: str
    message: str
    location: str | None = None


class PatentSummary(BaseModel):
    id: str
    title: str
    abstract: str
    assignee: str | None = None
    filing_date: str | None = None


class SearchResults(BaseModel):
    results: list[PatentSummary]
    total: int


class PatentDetail(PatentSummary):
    claims: list[str]
    inventors: list[str]
    classification: list[str]
    cited_patents: list[PatentSummary]

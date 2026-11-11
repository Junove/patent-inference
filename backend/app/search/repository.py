"""Repository interface (FR-S5): callers depend only on this, so a real patent
source can replace the seeded SQLite implementation without API changes."""
from abc import ABC, abstractmethod

from app.schemas import PatentDetail, PatentSummary


class PatentRepository(ABC):
    @abstractmethod
    def search(self, query: str, *, page: int = 1, page_size: int = 10, date_from: str | None = None,
               date_to: str | None = None, assignee: str | None = None, inventor: str | None = None,
               classification: str | None = None) -> tuple[list[PatentSummary], int]:
        """Return (results for this page, total matching count)."""

    @abstractmethod
    def get(self, patent_id: str) -> PatentDetail | None: ...

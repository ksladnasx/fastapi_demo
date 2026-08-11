from datetime import datetime

from sqlmodel import SQLModel


class RecruitmentJobRead(SQLModel):
    id: int
    source_site: str
    source_page: int | None = None
    company_name: str | None = None
    job_title: str | None = None
    location: str | None = None
    target_candidates: str | None = None
    position: str | None = None
    progress_status: str | None = None
    deadline: str | None = None
    official_url: str | None = None
    recruitment_url: str | None = None
    summary: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RecruitmentJobList(SQLModel):
    total: int
    page: int
    page_size: int
    items: list[RecruitmentJobRead]


class RecruitmentImportResult(SQLModel):
    fetched_pages: int
    parsed_items: int
    created: int
    updated: int

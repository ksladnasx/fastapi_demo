from datetime import datetime

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, SQLModel


class RecruitmentJob(SQLModel, table=True):
    __tablename__ = "recruitment_jobs"

    id: int | None = Field(default=None, primary_key=True)
    source_site: str = Field(default="givemeoc", max_length=50, index=True)
    source_page: int | None = Field(default=None, index=True)
    source_key: str = Field(max_length=64, unique=True, index=True)
    company_name: str | None = Field(default=None, max_length=255, index=True)
    job_title: str | None = Field(default=None, max_length=255, index=True)
    location: str | None = Field(default=None, max_length=255, index=True)
    target_candidates: str | None = Field(default=None, max_length=255)
    position: str | None = Field(default=None, max_length=255)
    progress_status: str | None = Field(default=None, max_length=255, index=True)
    deadline: str | None = Field(default=None, max_length=255)
    official_url: str | None = Field(default=None, max_length=1024)
    recruitment_url: str | None = Field(default=None, max_length=1024)
    summary: str | None = Field(default=None, sa_column=Column(Text))
    raw_html: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()),
    )

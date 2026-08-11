from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_
from sqlmodel import select

from app.db.manager import get_sync_db_session
from app.models.recruitment import RecruitmentJob


class RecruitmentJobDao:
    @classmethod
    def list(
        cls,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        location: str | None = None,
        progress_status: str | None = None,
    ) -> tuple[list[RecruitmentJob], int]:
        with get_sync_db_session() as session:
            statement = select(RecruitmentJob)
            count_statement = select(func.count()).select_from(RecruitmentJob)

            filters = []
            if keyword:
                pattern = f"%{keyword.strip()}%"
                filters.append(
                    or_(
                        RecruitmentJob.company_name.like(pattern),
                        RecruitmentJob.job_title.like(pattern),
                        RecruitmentJob.summary.like(pattern),
                    )
                )
            if location:
                filters.append(RecruitmentJob.location.like(f"%{location.strip()}%"))
            if progress_status:
                filters.append(
                    RecruitmentJob.progress_status.like(f"%{progress_status.strip()}%")
                )

            for condition in filters:
                statement = statement.where(condition)
                count_statement = count_statement.where(condition)

            total = session.exec(count_statement).one()
            offset = (page - 1) * page_size
            statement = (
                statement.order_by(RecruitmentJob.id.desc()).offset(offset).limit(page_size)
            )
            return list(session.exec(statement).all()), total

    @classmethod
    def upsert_many(cls, jobs_data: list[dict[str, Any]]) -> tuple[int, int]:
        created = 0
        updated = 0

        with get_sync_db_session() as session:
            for job_data in jobs_data:
                source_key = job_data["source_key"]
                statement = select(RecruitmentJob).where(
                    RecruitmentJob.source_key == source_key
                )
                existing = session.exec(statement).first()

                if existing:
                    for field, value in job_data.items():
                        setattr(existing, field, value)
                    session.add(existing)
                    updated += 1
                else:
                    session.add(RecruitmentJob.model_validate(job_data))
                    created += 1

            session.commit()

        return created, updated

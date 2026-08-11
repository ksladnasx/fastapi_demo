from app.crud.recruitment import RecruitmentJobDao
from app.models.recruitment import RecruitmentJob
from app.schemas.recruitment import RecruitmentJobList, RecruitmentJobRead


class RecruitmentService:
    @classmethod
    def list_jobs(
        cls,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        location: str | None = None,
        progress_status: str | None = None,
    ) -> RecruitmentJobList:
        jobs, total = RecruitmentJobDao.list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            location=location,
            progress_status=progress_status,
        )
        return RecruitmentJobList(
            total=total,
            page=page,
            page_size=page_size,
            items=[RecruitmentJobRead.model_validate(job) for job in jobs],
        )

    @classmethod
    def import_jobs(cls, jobs_data: list[dict]) -> tuple[int, int]:
        normalized = [cls._normalize_job(job) for job in jobs_data]
        return RecruitmentJobDao.upsert_many(normalized)

    @staticmethod
    def _normalize_job(job: dict) -> dict:
        allowed_fields = set(RecruitmentJob.model_fields)
        return {key: value for key, value in job.items() if key in allowed_fields}

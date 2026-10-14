from app.crud.recruitment import RecruitmentJobDao
from app.models.recruitment import RecruitmentJob
from app.schemas.recruitment import RecruitmentJobList, RecruitmentJobRead


class RecruitmentService:
    # 这里实际上就是  
    # def 函数(参数)->RecruitmentJobList(类型):
    #         jobs, total   =  RecruitmentJobDao.list(参数)
    @classmethod
    def list_jobs(
        cls,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        location: str | None = None,
        progress_status: str | None = None,
    ) -> RecruitmentJobList:   #返回值类型是 RecruitmentJobList
        # 调用数据库操作函数获取值
        jobs, total = RecruitmentJobDao.list(  #数据库访问函数
            page=page,
            page_size=page_size,
            keyword=keyword,
            location=location,
            progress_status=progress_status,
        )
        # Schema/Model 层的 RecruitmentJobList，用于数据校验和序列化
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

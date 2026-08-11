from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUserDep
from app.schemas.recruitment import RecruitmentImportResult, RecruitmentJobList
from app.schemas.response import ApiResponse
from app.services.givemeoc_scraper import crawl_givemeoc
from app.services.recruitment import RecruitmentService
from app.utils.common import success_response

router = APIRouter(prefix="/recruitment", tags=["recruitment"])


@router.get("/jobs", response_model=ApiResponse[RecruitmentJobList])
def list_jobs(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    keyword: str | None = None,
    location: str | None = None,
    progress_status: str | None = None,
):
    jobs = RecruitmentService.list_jobs(
        page=page,
        page_size=page_size,
        keyword=keyword,
        location=location,
        progress_status=progress_status,
    )
    return success_response(data=jobs, code=0)


@router.post("/import/givemeoc", response_model=ApiResponse[RecruitmentImportResult])
def import_givemeoc_jobs(
    current_user: CurrentUserDep,
    pages: Annotated[int, Query(ge=1, le=100)] = 30,
    start_page: Annotated[int, Query(ge=1)] = 1,
):
    jobs = crawl_givemeoc(start_page=start_page, pages=pages)
    created, updated = RecruitmentService.import_jobs(jobs)
    return success_response(
        data=RecruitmentImportResult(
            fetched_pages=pages,
            parsed_items=len(jobs),
            created=created,
            updated=updated,
        ),
        message="GivemeOC jobs imported successfully",
        code=0,
    )

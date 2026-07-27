from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100


def get_pagination(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)


PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]

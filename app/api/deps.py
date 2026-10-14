from typing import Annotated

from fastapi import Cookie, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import decode_access_token
from app.crud.user import UserDao
from app.exceptions import UnauthorizedException
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]


def get_user_from_access_token(token: str | None) -> User:
    if not token:
        raise UnauthorizedException("Missing access token")

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired access token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid access token")

    try:
        user = UserDao.get(int(user_id))
    except (TypeError, ValueError):
        raise UnauthorizedException("Invalid access token") from None
    if not user or not user.is_active:
        raise UnauthorizedException("Invalid access token")

    return user


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise UnauthorizedException("Missing access token")
    return get_user_from_access_token(credentials.credentials)


def get_current_user_from_cookie(
    session_token: Annotated[str | None, Cookie(alias=settings.SESSION_COOKIE_NAME)] = None,
) -> User:
    return get_user_from_access_token(session_token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
CookieCurrentUserDep = Annotated[User, Depends(get_current_user_from_cookie)]

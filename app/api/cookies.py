from fastapi import APIRouter, Response, status

from app.api.deps import CookieCurrentUserDep
from app.core.config import settings
from app.schemas.response import ApiResponse
from app.schemas.user import TokenRead, UserLogin, UserRead
from app.services.user import UserService
from app.utils.common import success_response

router = APIRouter(prefix="/cookie", tags=["cookie-demo"])


@router.post("/login", response_model=ApiResponse[UserRead])
def login_with_cookie(login_data: UserLogin, response: Response):
    """Set an HttpOnly session cookie through the Set-Cookie response header."""
    token: TokenRead = UserService.login(login_data)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token.access_token,
        max_age=token.expires_in,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return success_response(
        data=token.user,
        message=(
            "Cookie login successfully. Browser received an HttpOnly session cookie "
            "from the Set-Cookie response header."
        ),
    )


@router.get("/me", response_model=ApiResponse[UserRead])
def get_me_from_cookie(current_user: CookieCurrentUserDep):
    """Read the current user from the session cookie sent by the browser."""
    return success_response(
        data=current_user,
        message="Current user was loaded from the session cookie.",
    )


@router.post("/logout", response_model=ApiResponse[None])
def logout_from_cookie(response: Response):
    """Delete the session cookie by sending an expired Set-Cookie header."""
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        samesite="lax",
    )
    return success_response(message="Cookie logout successfully. Session cookie was deleted.")


@router.post("/visible", response_model=ApiResponse[dict[str, str]])
def set_visible_cookie(response: Response):
    """Set a non-HttpOnly cookie so the frontend can read it with document.cookie."""
    response.set_cookie(
        key=settings.VISIBLE_COOKIE_NAME,
        value="hello-from-fastapi",
        max_age=3600,
        httponly=False,
        samesite="lax",
        secure=False,
        path="/",
    )
    return success_response(
        data={
            "cookie_name": settings.VISIBLE_COOKIE_NAME,
            "cookie_value": "hello-from-fastapi",
        },
        message="A visible cookie was set. You can read it with document.cookie.",
    )


@router.delete("/visible", response_model=ApiResponse[None], status_code=status.HTTP_200_OK)
def clear_visible_cookie(response: Response):
    response.delete_cookie(
        key=settings.VISIBLE_COOKIE_NAME,
        path="/",
        samesite="lax",
    )
    return success_response(message="Visible cookie was deleted.")

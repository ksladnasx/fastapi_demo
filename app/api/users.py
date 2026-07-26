from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.crud.user import UserCRUD
from app.db.session import get_session
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),  # noqa: B008
):
    existing = UserCRUD.get_user_by_username(session, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing = UserCRUD.get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return UserCRUD.create_user(session, user_data)


@router.get("/", response_model=list[UserRead])
def get_users(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    session: Session = Depends(get_session),
):
    return UserCRUD.get_users(session, skip=skip, limit=limit, is_active=is_active)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = UserCRUD.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
):
    if user_data.username:
        existing = UserCRUD.get_user_by_username(session, user_data.username)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

    if user_data.email:
        existing = UserCRUD.get_user_by_email(session, user_data.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    user = UserCRUD.update_user(session, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    if not UserCRUD.delete_user(session, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

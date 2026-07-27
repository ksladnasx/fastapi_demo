from fastapi import APIRouter, HTTPException, status

from app.models.user import UserDao
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate):
    try:
        return UserDao.create(user_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[UserRead])
def get_users(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
):
    return UserDao.list(skip=skip, limit=limit, is_active=is_active)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    user = UserDao.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_data: UserUpdate):
    try:
        user = UserDao.update(user_id, user_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    if not UserDao.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

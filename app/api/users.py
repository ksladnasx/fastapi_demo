from fastapi import APIRouter, status

from app.api.deps import PaginationDep
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate):
    return UserService.create_user(user_data)


@router.get("/", response_model=list[UserRead])
def get_users(
    pagination: PaginationDep,
    is_active: bool | None = None,
):
    return UserService.list_users(
        page=pagination.page,
        page_size=pagination.page_size,
        is_active=is_active,
    )


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    return UserService.get_user(user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_data: UserUpdate):
    return UserService.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    UserService.delete_user(user_id)

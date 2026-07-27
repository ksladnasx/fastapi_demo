from fastapi import APIRouter, status

from app.api.deps import PaginationDep
from app.schemas.response import ApiResponse
from app.schemas.user import TokenRead, UserCreate, UserLogin, UserRead, UserUpdate
from app.services.user import UserService
from app.utils.common import success_response

router = APIRouter(prefix="/user", tags=["users"])


@router.post(
    "/register",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserCreate):
    user = UserService.register(user_data)
    return success_response(data=user, message="Register successfully")


@router.post("/login", response_model=ApiResponse[TokenRead])
def login(login_data: UserLogin):
    token = UserService.login(login_data)
    return success_response(data=token, message="Login successfully")


@router.post(
    "/create_user",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
def create_user(user_data: UserCreate):
    user = UserService.create_user(user_data)
    return success_response(data=user, message="User created successfully")


@router.post(
    "/create_users",
    response_model=ApiResponse[list[UserRead]],
    status_code=status.HTTP_201_CREATED,
)
def create_users(users_data: list[UserCreate]):
    users = UserService.create_users(users_data)
    return success_response(data=users, message="Users created successfully")


@router.get("/get_users", response_model=ApiResponse[list[UserRead]])
def get_users(
    pagination: PaginationDep,
    is_active: bool | None = None,
):
    users = UserService.list_users(
        page=pagination.page,
        page_size=pagination.page_size,
        is_active=is_active,
    )
    return success_response(data=users)


@router.get("/get/{user_id}", response_model=ApiResponse[UserRead])
def get_user(user_id: int):
    user = UserService.get_user(user_id)
    return success_response(data=user)


@router.put("/put/{user_id}", response_model=ApiResponse[UserRead])
def update_user(user_id: int, user_data: UserUpdate):
    user = UserService.update_user(user_id, user_data)
    return success_response(data=user, message="User updated successfully")


@router.delete("/del/{user_id}", response_model=ApiResponse[None])
def delete_user(user_id: int):
    UserService.delete_user(user_id)
    return success_response(message="User deleted successfully")

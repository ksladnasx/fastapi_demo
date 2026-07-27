from app.crud.user import UserDao
from app.exceptions import BadRequestException, NotFoundException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.common import normalize_email


class UserService:
    @classmethod
    def create_user(cls, user_data: UserCreate) -> User:
        user_data.email = normalize_email(user_data.email)

        if UserDao.get_by_username(user_data.username):
            raise BadRequestException("Username already registered")

        if UserDao.get_by_email(user_data.email):
            raise BadRequestException("Email already registered")

        return UserDao.create(user_data)
    @classmethod
    def create_users(cls, users_data: list[UserCreate]) -> list[User]:
        created_users = []
        for user_data in users_data:
            user_data.email = normalize_email(user_data.email)

            if UserDao.get_by_username(user_data.username):
                raise BadRequestException(f"Username '{user_data.username}' already registered")

            if UserDao.get_by_email(user_data.email):
                raise BadRequestException(f"Email '{user_data.email}' already registered")

            created_user = UserDao.create(user_data)
            created_users.append(created_user)

        return created_users
    @classmethod
    def list_users(
        cls,
        page: int = 1,
        page_size: int = 10,
        is_active: bool | None = None,
    ) -> list[User]:
        return UserDao.list(page=page, page_size=page_size, is_active=is_active)

    @classmethod
    def get_user(cls, user_id: int) -> User:
        user = UserDao.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    @classmethod
    def update_user(cls, user_id: int, user_data: UserUpdate) -> User:
        update_data = user_data.model_dump(exclude_unset=True)

        username = update_data.get("username")
        if username:
            existing = UserDao.get_by_username(username)
            if existing and existing.id != user_id:
                raise BadRequestException("Username already registered")

        email = update_data.get("email")
        if email:
            user_data.email = normalize_email(email)
            existing = UserDao.get_by_email(user_data.email)
            if existing and existing.id != user_id:
                raise BadRequestException("Email already registered")

        user = UserDao.update(user_id, user_data)
        if not user:
            raise NotFoundException("User not found")
        return user

    @classmethod
    def delete_user(cls, user_id: int) -> None:
        if not UserDao.delete(user_id):
            raise NotFoundException("User not found")

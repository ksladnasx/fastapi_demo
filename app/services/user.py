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
    def list_users(
        cls,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list[User]:
        return UserDao.list(skip=skip, limit=limit, is_active=is_active)

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

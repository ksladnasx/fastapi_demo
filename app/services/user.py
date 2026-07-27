from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.crud.user import UserDao
from app.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.models.user import User
from app.schemas.user import TokenRead, UserCreate, UserLogin, UserRead, UserUpdate
from app.utils.common import normalize_email


class UserService:
    @classmethod
    def create_user(cls, user_data: UserCreate) -> User:
        email = normalize_email(user_data.email)

        if UserDao.get_by_username(user_data.username):
            raise BadRequestException("用户名已存在")

        if UserDao.get_by_email(email):
            raise BadRequestException("邮箱已被注册")

        create_data = user_data.model_dump(exclude={"password"})
        create_data["email"] = email
        create_data["password_hash"] = hash_password(user_data.password)
        return UserDao.create(create_data)

    @classmethod
    def register(cls, user_data: UserCreate) -> User:
        return cls.create_user(user_data)

    @classmethod
    def login(cls, login_data: UserLogin) -> TokenRead:
        account = login_data.username.strip()
        user = UserDao.get_by_username(account) or UserDao.get_by_email(
            normalize_email(account)
        )

        if not user or not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException("用户名或密码错误")

        if not user.is_active:
            raise UnauthorizedException("用户已被禁用")

        return TokenRead(
            access_token=create_access_token(str(user.id)),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserRead.model_validate(user),
        )

    @classmethod
    def create_users(cls, users_data: list[UserCreate]) -> list[User]:
        created_users = []
        for user_data in users_data:
            created_users.append(cls.create_user(user_data))

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
            email = normalize_email(email)
            existing = UserDao.get_by_email(email)
            if existing and existing.id != user_id:
                raise BadRequestException("Email already registered")
            update_data["email"] = email

        password = update_data.pop("password", None)
        if password:
            update_data["password_hash"] = hash_password(password)

        user = UserDao.update(user_id, update_data)
        if not user:
            raise NotFoundException("User not found")
        return user

    @classmethod
    def delete_user(cls, user_id: int) -> None:
        if not UserDao.delete(user_id):
            raise NotFoundException("User not found")

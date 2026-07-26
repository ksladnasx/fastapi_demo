from typing import Optional

from sqlmodel import Session, select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserCRUD:
    @staticmethod
    def get_user(session: Session, user_id: int) -> Optional[User]:
        return session.get(User, user_id)

    @staticmethod
    def get_user_by_username(session: Session, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()

    @staticmethod
    def get_users(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> list[User]:
        statement = select(User)

        if is_active is not None:
            statement = statement.where(User.is_active == is_active)

        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_user_count(session: Session) -> int:
        statement = select(User)
        return len(session.exec(statement).all())

    @staticmethod
    def create_user(session: Session, user_data: UserCreate) -> User:
        user = User.model_validate(user_data)

        try:
            session.add(user)
            session.commit()
            session.refresh(user)
        except Exception:
            session.rollback()
            raise

        return user

    @staticmethod
    def update_user(
        session: Session,
        user_id: int,
        user_data: UserUpdate,
    ) -> Optional[User]:
        user = session.get(User, user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            session.add(user)
            session.commit()
            session.refresh(user)
        except Exception:
            session.rollback()
            raise

        return user

    @staticmethod
    def delete_user(session: Session, user_id: int) -> bool:
        user = session.get(User, user_id)
        if not user:
            return False

        try:
            session.delete(user)
            session.commit()
        except Exception:
            session.rollback()
            raise

        return True

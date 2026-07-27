from typing import Any

from sqlmodel import Session, select

from app.db.manager import get_sync_db_session
from app.models.user import User


class UserDao:
    @classmethod
    def get(cls, user_id: int) -> User | None:
        with get_sync_db_session() as session:
            return session.get(User, user_id)

    @classmethod
    def get_by_username(cls, username: str) -> User | None:
        with get_sync_db_session() as session:
            return cls._get_by_username(session, username)

    @classmethod
    def get_by_email(cls, email: str) -> User | None:
        with get_sync_db_session() as session:
            return cls._get_by_email(session, email)

    @classmethod
    def list(
        cls,
        page: int = 1,
        page_size: int = 10,
        is_active: bool | None = None,
    ) -> list[User]:
        with get_sync_db_session() as session:
            statement = select(User)

            if is_active is not None:
                statement = statement.where(User.is_active == is_active)

            offset = (page - 1) * page_size
            statement = statement.offset(offset).limit(page_size)
            return list(session.exec(statement).all())

    @classmethod
    def create(cls, user_data: Any) -> User:
        with get_sync_db_session() as session:
            user = User.model_validate(user_data)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @classmethod
    def update(cls, user_id: int, user_data: Any) -> User | None:
        with get_sync_db_session() as session:
            user = session.get(User, user_id)
            if not user:
                return None

            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @classmethod
    def delete(cls, user_id: int) -> bool:
        with get_sync_db_session() as session:
            user = session.get(User, user_id)
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True

    @staticmethod
    def _get_by_username(session: Session, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

    @staticmethod
    def _get_by_email(session: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()

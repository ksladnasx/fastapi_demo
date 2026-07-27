from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel, select


class UserBase(SQLModel):
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True)
    full_name: str | None = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, onupdate=func.now()),
    )

    @classmethod
    def get(cls, user_id: int) -> "User | None":
        from app.db.session import get_sync_db_session

        with get_sync_db_session() as session:
            return session.get(cls, user_id)

    @classmethod
    def get_by_username(cls, username: str) -> "User | None":
        from app.db.session import get_sync_db_session

        with get_sync_db_session() as session:
            statement = select(cls).where(cls.username == username)
            return session.exec(statement).first()

    @classmethod
    def get_by_email(cls, email: str) -> "User | None":
        from app.db.session import get_sync_db_session

        with get_sync_db_session() as session:
            statement = select(cls).where(cls.email == email)
            return session.exec(statement).first()

    @classmethod
    def list(
        cls,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list["User"]:
        from app.db.session import get_sync_db_session

        with get_sync_db_session() as session:
            statement = select(cls)

            if is_active is not None:
                statement = statement.where(cls.is_active == is_active)

            statement = statement.offset(skip).limit(limit)
            return list(session.exec(statement).all())

    @classmethod
    def create(cls, user_data: Any) -> "User":
        from app.db.session import get_sync_db_session

        with get_sync_db_session() as session:
            if cls._get_by_username(session, user_data.username):
                raise ValueError("Username already registered")

            if cls._get_by_email(session, user_data.email):
                raise ValueError("Email already registered")

            user = cls.model_validate(user_data)

            try:
                session.add(user)
                session.commit()
                session.refresh(user)
            except Exception:
                session.rollback()
                raise

            return user

    @classmethod
    def update(cls, user_id: int, user_data: Any) -> "User | None":
        from app.db.session import get_sync_db_session

        with get_sync_db_session() as session:
            user = session.get(cls, user_id)
            if not user:
                return None

            update_data = user_data.model_dump(exclude_unset=True)

            username = update_data.get("username")
            if username:
                existing = cls._get_by_username(session, username)
                if existing and existing.id != user_id:
                    raise ValueError("Username already registered")

            email = update_data.get("email")
            if email:
                existing = cls._get_by_email(session, email)
                if existing and existing.id != user_id:
                    raise ValueError("Email already registered")

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

    @classmethod
    def delete(cls, user_id: int) -> bool:
        from app.db.session import get_sync_db_session

        with get_sync_db_session() as session:
            user = session.get(cls, user_id)
            if not user:
                return False

            try:
                session.delete(user)
                session.commit()
            except Exception:
                session.rollback()
                raise

            return True

    @classmethod
    def _get_by_username(cls, session, username: str) -> "User | None":
        statement = select(cls).where(cls.username == username)
        return session.exec(statement).first()

    @classmethod
    def _get_by_email(cls, session, email: str) -> "User | None":
        statement = select(cls).where(cls.email == email)
        return session.exec(statement).first()

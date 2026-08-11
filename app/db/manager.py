from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, select

from app.db.connection import DatabaseConnection, db_connection


class DatabaseManager:
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection

    @property
    def engine(self) -> Engine:
        return self.connection.engine

    def init_db(self) -> None:
        from app.models import RecruitmentJob, User  # noqa: F401

        SQLModel.metadata.create_all(self.engine)

    def close(self) -> None:
        self.connection.dispose()

    def health_check(self) -> bool:
        with get_sync_db_session() as session:
            return session.exec(select(1)).first() == 1

    def pool_status(self) -> str:
        return self.connection.pool_status()


db_manager = DatabaseManager(db_connection)


@contextmanager
def get_sync_db_session() -> Generator[Session, None, None]:
    with Session(db_manager.engine) as session:
        yield session


def init_db() -> None:
    db_manager.init_db()

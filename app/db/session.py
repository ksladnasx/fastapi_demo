from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
)


@contextmanager
def get_sync_db_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def init_db():
    from app.models import User  # noqa: F401

    SQLModel.metadata.create_all(engine)

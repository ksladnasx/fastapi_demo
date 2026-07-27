from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from app.core.config import settings

'''
数据库连接管理器
负责管理数据库引擎的创建、连接池配置和生命周期管理
'''
  
class DatabaseConnection:
    def __init__(self) -> None:
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
        return self._engine

    def dispose(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    def pool_status(self) -> str:
        return self.engine.pool.status()


db_connection = DatabaseConnection()

# SQLAlchemy 的 Engine 类型，代表数据库引擎（内部含连接池）
from sqlalchemy.engine import Engine

# SQLModel 提供的 create_engine，底层就是 SQLAlchemy 的 create_engine
from sqlmodel import create_engine

# 项目配置：从 settings 中读取数据库 URL、是否打印 SQL 等
from app.core.config import settings


class DatabaseConnection:
    """
    数据库连接封装类。

    核心特点：延迟初始化（lazy init）。
    - 实例创建时不会马上建引擎/连接池；
    - 第一次访问 engine 属性时才真正创建；
    - 便于按需启动、避免导入时就连库。
    """

    def __init__(self) -> None:
        # 保存引擎实例，初始为 None，表示尚未创建
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        # 首次访问时创建引擎（懒加载）
        if self._engine is None:
            self._engine = create_engine(
                # 数据库连接字符串，如 mysql+pymysql://user:pwd@host/db
                settings.DATABASE_URL,
                # 是否把执行的 SQL 打印到日志，调试用；生产一般关掉
                echo=settings.DATABASE_ECHO,
                # 从连接池取连接前先 ping 一下，避免拿到已失效的连接
                pool_pre_ping=True,
                # 连接存活超过 3600 秒就回收，防止被数据库/中间件断开
                pool_recycle=3600,
            )
        return self._engine

    def dispose(self) -> None:
        # 关闭连接池、释放所有连接
        if self._engine is not None:
            self._engine.dispose()
            # 重置为 None，下次访问 engine 会重新创建
            self._engine = None

    def pool_status(self) -> str:
        # 返回连接池状态字符串，例如：
        # "Pool size: 5  Connections in pool: 0 ..."
        # 访问 self.engine 会触发懒加载
        return self.engine.pool.status()


# 全局单例：整个应用共用一个 DatabaseConnection
db_connection = DatabaseConnection()
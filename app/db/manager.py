# 从 collections.abc 导入 Generator，用于类型注解：
# 说明下面的 get_sync_db_session 是一个生成器函数
from collections.abc import Generator

# contextmanager 用来把“生成器函数”装饰成“上下文管理器”
# 这样就能写成 with get_sync_db_session() as session:
from contextlib import contextmanager

# SQLAlchemy 的 Engine 类型，代表数据库引擎/连接池入口
from sqlalchemy.engine import Engine

# SQLModel 相关：
# Session：同步数据库会话
# SQLModel：ORM 基类，metadata 里保存所有模型表结构
# select：构造查询语句
from sqlmodel import Session, SQLModel, select

# 项目内部的数据库连接封装：
# DatabaseConnection：底层连接管理类
# db_connection：已经创建好的全局数据库连接实例
from app.db.connection import DatabaseConnection, db_connection


class DatabaseManager:
    """
    数据库管理器。
    它不直接创建连接，而是包装 DatabaseConnection，
    对外提供 engine、初始化表、健康检查、连接池状态、关闭等能力。
    """

    def __init__(self, connection: DatabaseConnection) -> None:
        # 保存底层数据库连接对象
        self.connection = connection

    @property
    def engine(self) -> Engine:
        # 代理属性：外部可以通过 db_manager.engine 拿到 SQLAlchemy Engine
        return self.connection.engine

    def init_db(self) -> None:
        # 延迟导入模型。不导入的话永远不会触发 SQLModel/SQLAlchemy 的注册逻辑
        # 这里导入 User 并不是为了使用它，而是为了让 User 模型注册到
        # SQLModel.metadata 中。否则 create_all 可能不知道要建 User 表。
        # noqa: F401 表示告诉 linter 忽略“导入了但未使用”的警告。
        from app.models import Item, User  # noqa: F401

        # 根据 SQLModel.metadata 中登记的所有模型，在数据库中创建表。
        # 如果表已经存在，默认会跳过。
        SQLModel.metadata.create_all(self.engine)

    def close(self) -> None:
        # 释放底层连接资源，通常应用关闭时调用
        self.connection.dispose()

    def health_check(self) -> bool:
        # 健康检查：打开一个数据库会话，执行 SELECT 1
        # 如果返回的第一行结果是 1，说明数据库连接正常。
        with get_sync_db_session() as session:
            return session.exec(select(1)).first() == 1  # type: ignore[call-overload]

    def pool_status(self) -> str:
        # 返回底层连接池状态，具体格式由 DatabaseConnection 决定
        return self.connection.pool_status()


# 创建全局数据库管理器实例。
# 其他模块可以直接 from xxx import db_manager 使用。
db_manager = DatabaseManager(db_connection)


@contextmanager
def get_sync_db_session() -> Generator[Session, None, None]:
    """
    同步数据库 Session 的上下文管理器。

    用法：
        with get_sync_db_session() as session:
            session.exec(...)

    退出 with 代码块时，Session 会自动关闭。
    """
    # 创建 SQLModel 的同步 Session，并绑定到全局 db_manager 的 engine
    with Session(db_manager.engine) as session:
        # 把 session 交给调用方使用
        yield session


def init_db() -> None:
    # 模块级初始化入口，方便外部直接调用 init_db()
    # 实际逻辑交给全局 db_manager 处理
    db_manager.init_db()
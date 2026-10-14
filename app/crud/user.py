from typing import Any

from sqlmodel import Session, select

from app.db.manager import get_sync_db_session
from app.models.user import User


#对用户的数据库操作函数
class UserDao:
    # cls 是 类方法（classmethod）的第一个参数，代表类本身，你想怎么取名都行
    # 就像实例方法的第一个参数 self 代表实例本身。
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

            update_data = (
                user_data
                if isinstance(user_data, dict)
                else user_data.model_dump(exclude_unset=True)
            )
            for field, value in update_data.items():
                setattr(user, field, value)

            session.add(user)  #添加记录
            session.commit()  #提交更改
            session.refresh(user) #将数据库的信息同步到实例上
            return user

    @classmethod
    def delete(cls, user_id: int) -> bool:
        with get_sync_db_session() as session:
            #先通过查询找到需要删除的记录
            user = session.get(User, user_id)
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True

    @staticmethod
    def _get_by_username(session: Session, username: str) -> User | None:
        #对于查询较为复杂条件的情况
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

    @staticmethod
    def _get_by_email(session: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()

# 数据库的模型和 Pydantic 模式之间的桥梁
from datetime import datetime

from sqlmodel import SQLModel

from app.models.user import UserBase


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

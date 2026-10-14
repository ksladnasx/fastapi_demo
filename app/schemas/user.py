from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.user import UserBase


# 继承 SQLModel 的作用是继承了两套能力，在这里的话是为了
# Pydantic 的 BaseModel：数据校验、序列化、类型转换
# 用于响应体的格式校验
# 它是一个“数据模型”，但不是“表模型”
class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserLogin(SQLModel):
    username: str
    password: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None


class TokenRead(SQLModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead

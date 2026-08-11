from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.user import UserBase


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

class itemRead(SQLModel):
    id: int
    name: str
    description: str | None = None
    price: float
    created_at: datetime
    updated_at: datetime | None = None

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.item import ItemBase


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    counts: int | None = Field(default=None, ge=0)
    price: float | None = Field(default=None, ge=0)


class ItemRead(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime | None = None


class ItemList(SQLModel):
    username: str
    page: int
    page_size: int
    total: int
    items: list[ItemRead]

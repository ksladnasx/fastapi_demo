from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class ItemBase(SQLModel):
    name: str = Field(max_length=50, index=True)
    description: str | None = Field(default=None, max_length=255)
    counts: int = Field(default=0, ge=0)
    price: float = Field(default=0, ge=0)


class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()),
    )

    owner: "User" = Relationship(back_populates="items")

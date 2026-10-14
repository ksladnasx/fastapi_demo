from typing import Any

from sqlalchemy import func
from sqlmodel import select

from app.db.manager import get_sync_db_session
from app.models.item import Item


class ItemDao:
    @classmethod
    def create(cls, item_data: Any) -> Item:
        with get_sync_db_session() as session:
            item = Item.model_validate(item_data)
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    @classmethod
    def get(cls, item_id: int) -> Item | None:
        with get_sync_db_session() as session:
            return session.get(Item, item_id)

    @classmethod
    def list_by_owner_id(
        cls,
        owner_id: int,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Item], int]:
        with get_sync_db_session() as session:
            total_statement = select(func.count()).select_from(Item).where(
                Item.owner_id == owner_id
            )
            total = session.exec(total_statement).one()

            offset = (page - 1) * page_size
            statement = (
                select(Item)
                .where(Item.owner_id == owner_id)
                .order_by(Item.id.desc())
                .offset(offset)
                .limit(page_size)
            )
            items = list(session.exec(statement).all())
            return items, total

    @classmethod
    def update(cls, item_id: int, item_data: Any) -> Item | None:
        with get_sync_db_session() as session:
            item = session.get(Item, item_id)
            if not item:
                return None

            update_data = (
                item_data
                if isinstance(item_data, dict)
                else item_data.model_dump(exclude_unset=True)
            )
            for field, value in update_data.items():
                setattr(item, field, value)

            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    @classmethod
    def delete(cls, item_id: int) -> bool:
        with get_sync_db_session() as session:
            item = session.get(Item, item_id)
            if not item:
                return False

            session.delete(item)
            session.commit()
            return True

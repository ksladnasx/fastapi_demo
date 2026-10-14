from app.crud.item import ItemDao
from app.crud.user import UserDao
from app.exceptions import NotFoundException, UnauthorizedException
from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemList, ItemRead, ItemUpdate


class ItemService:
    @classmethod
    def create_item(cls, item_data: ItemCreate, current_user: User) -> Item:
        create_data = item_data.model_dump()
        create_data["owner_id"] = current_user.id
        return ItemDao.create(create_data)

    @classmethod
    def list_items_by_username(
        cls,
        username: str,
        page: int = 1,
        page_size: int = 10,
    ) -> ItemList:
        user = UserDao.get_by_username(username)
        if not user:
            raise NotFoundException("User not found")

        items, total = ItemDao.list_by_owner_id(
            owner_id=user.id,
            page=page,
            page_size=page_size,
        )
        return ItemList(
            username=user.username,
            page=page,
            page_size=page_size,
            total=total,
            items=[ItemRead.model_validate(item) for item in items],
        )

    @classmethod
    def list_my_items(
        cls,
        current_user: User,
        page: int = 1,
        page_size: int = 10,
    ) -> ItemList:
        return cls.list_items_by_username(
            username=current_user.username,
            page=page,
            page_size=page_size,
        )

    @classmethod
    def get_item(cls, item_id: int, current_user: User) -> Item:
        item = ItemDao.get(item_id)
        if not item:
            raise NotFoundException("Item not found")
        if item.owner_id != current_user.id:
            raise UnauthorizedException("You can only access your own items")
        return item

    @classmethod
    def update_item(
        cls,
        item_id: int,
        item_data: ItemUpdate,
        current_user: User,
    ) -> Item:
        cls.get_item(item_id, current_user)
        item = ItemDao.update(item_id, item_data)
        if not item:
            raise NotFoundException("Item not found")
        return item

    @classmethod
    def delete_item(cls, item_id: int, current_user: User) -> None:
        cls.get_item(item_id, current_user)
        if not ItemDao.delete(item_id):
            raise NotFoundException("Item not found")

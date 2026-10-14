from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUserDep, PaginationDep
from app.schemas.item import ItemCreate, ItemList, ItemRead, ItemUpdate
from app.schemas.response import ApiResponse
from app.services.items import ItemService
from app.utils.common import success_response

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ApiResponse[ItemRead], status_code=status.HTTP_201_CREATED)
def create_item(item_data: ItemCreate, current_user: CurrentUserDep):
    item = ItemService.create_item(item_data, current_user)
    return success_response(data=item, message="Item created successfully")


@router.get("/me", response_model=ApiResponse[ItemList])
def get_my_items(
    pagination: PaginationDep,
    current_user: CurrentUserDep,
):
    items = ItemService.list_my_items(
        current_user=current_user,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return success_response(data=items, message="Items retrieved successfully", code=0)


@router.get("/by-user/{username}", response_model=ApiResponse[ItemList])
def get_items_by_username(
    username: str,
    pagination: PaginationDep,
    current_user: CurrentUserDep,
):
    items = ItemService.list_items_by_username(
        username=username,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return success_response(data=items, message="Items retrieved successfully", code=0)


@router.get("/{item_id}", response_model=ApiResponse[ItemRead])
def get_item(item_id: int, current_user: CurrentUserDep):
    item = ItemService.get_item(item_id, current_user)
    return success_response(data=item, message="Item retrieved successfully", code=0)


@router.put("/{item_id}", response_model=ApiResponse[ItemRead])
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: CurrentUserDep,
):
    item = ItemService.update_item(item_id, item_data, current_user)
    return success_response(data=item, message="Item updated successfully")


@router.delete("/{item_id}", response_model=ApiResponse[None])
def delete_item(item_id: int, current_user: CurrentUserDep):
    ItemService.delete_item(item_id, current_user)
    return success_response(message="Item deleted successfully")

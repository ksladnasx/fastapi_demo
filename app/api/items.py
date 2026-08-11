from fastapi import APIRouter

from app.schemas.response import ApiResponse
from app.schemas.user import itemRead
from app.services.items import ItemService
from app.utils.common import success_response

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/get_items", response_model=ApiResponse[itemRead])
def get_items(
   
):
    items = ItemService.get_items()
    return success_response(data=items, message="Items retrieved successfully")
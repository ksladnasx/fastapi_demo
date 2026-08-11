from app.utils.common import get_current_time


class ItemService:
    @staticmethod
    def get_items():
        time = get_current_time()
        return {
            "id": 1,
            "name": "物品",
            "description": "这是一个物品",
            "price": 1.2,
            "created_at": time,
            "updated_at": time,
        }

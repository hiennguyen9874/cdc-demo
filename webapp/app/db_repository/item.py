from app.db_models import Item

from .base import BaseDbRepository


class ItemDbRepository(BaseDbRepository[Item]):
    pass


item_db_repository = ItemDbRepository(model=Item)

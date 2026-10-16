from pydantic import BaseModel

from dungeon_game.domain.actors.player.inventory_items import InventoryItem
from dungeon_game.domain.intent import ShopItemName


class Merchandise(BaseModel):
    """Something the merchant sells: its name, price, quantity,
    and the inventory item."""

    type: ShopItemName
    name: str
    price: int
    quantity: int
    item: InventoryItem

    def is_called(self, item: ShopItemName) -> bool:
        return self.type == item

    def cost_of(self, quantity: int) -> int:
        return self.price * quantity

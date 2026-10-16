from typing import Self

from pydantic import BaseModel

from dungeon_game.domain.actors.merchant.merchandise import (
    Merchandise,
)
from dungeon_game.domain.actors.player.inventory_items import (
    POTION,
    STEEL_SHIELD,
    STEEL_SWORD,
    InventoryItem,
)
from dungeon_game.domain.actors.player.warrior import Shield, Sword
from dungeon_game.domain.intent import ShopItem


class Merchant(BaseModel):
    """Everything that could be sold and how many of each are left. Anything
    not for sale has a quantity of zero."""

    merchandise: list[Merchandise]

    def has_item_in_stock(self, item_type: ShopItem | None) -> bool:
        return item_type is not None and self.is_in_stock(item_type, 1)

    def is_in_stock(self, item_type: ShopItem, quantity: int) -> bool:
        return any(
            m.type == item_type and m.quantity >= quantity for m in self.merchandise
        )

    def total_price(self, item_type: ShopItem, quantity: int) -> int:
        item = self._find_merchandise(item_type)
        if item is None:
            return -1
        return item.price * quantity

    def quantity_of(self, item_type: ShopItem) -> int:
        item = self._find_merchandise(item_type)
        if item is None:
            return 0
        return item.quantity

    def name_of(self, item_type: ShopItem) -> str:
        item = self._find_merchandise(item_type)
        if item is None:
            return item_type
        return item.name

    def with_item_removed(
        self, item_type: ShopItem, quantity: int
    ) -> tuple[Self, InventoryItem]:
        merchandise = self._find_merchandise(item_type)
        if merchandise is None:
            raise Exception("can't remove non-existent item")
        new_merchant = Merchant(merchandise=self._update_inventory(item_type, quantity))
        return new_merchant, merchandise.item

    def _update_inventory(
        self, item_type: ShopItem, quantity: int
    ) -> list[Merchandise]:
        updated_merchandise = []
        for item in self.merchandise:
            if item.type == item_type:
                item = item.model_copy(update={"quantity": item.quantity - quantity})
            updated_merchandise.append(item)
        return updated_merchandise

    def _find_merchandise(self, item_type: ShopItem) -> Merchandise | None:
        return next((m for m in self.merchandise if m.type == item_type), None)

    def describe_inventory(self) -> list[str]:
        """What is for sale."""
        lines = []
        for item in self.merchandise:
            if item.quantity == 1:
                lines.append(
                    f"The merchant has one {item.name} at a price of "
                    f"{item.price} gold coins."
                )
            elif item.quantity > 1:
                lines.append(
                    f"The merchant has {item.quantity} of {item.name} at a price "
                    f"of {item.price} gold coins each."
                )
        if len(lines) == 0:
            lines.append("The merchant is out of items to sell.")
        return lines


def create_merchant_for_warrior() -> Merchant:
    return Merchant(
        merchandise=[
            Merchandise(type="potion", name="potion", price=5, quantity=3, item=POTION),
            Merchandise(
                type="sword",
                name="steel sword",
                price=10,
                quantity=1,
                item=STEEL_SWORD,
            ),
            Merchandise(
                type="shield",
                name="steel shield",
                price=10,
                quantity=1,
                item=STEEL_SHIELD,
            ),
        ]
    )

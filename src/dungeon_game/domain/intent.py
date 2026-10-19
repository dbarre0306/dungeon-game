from typing import Literal

from pydantic import BaseModel, Field

IntentType = Literal[
    "explore",
    "look",
    "attack",
    "shop",
    "drink_potion",
    "cast_healing",
    "open_chest",
    "multiple",
    "unknown",
]
ExploreDirection = Literal["left", "right", "forward", "backward"]
ChestSide = Literal["left", "right"]
AttackTarget = Literal["enemy", "self", "other"]
ShopItemName = Literal["potion", "sword", "shield", "elder_staff"]


class Intent(BaseModel):
    """The explore_direction is always set when the type is `explore`.
    The chest_side is set when the type is `open_chest` and the player
    said which chest to open. The shop_item_name is set when the type is `shop`
    and the player said what they want to buy. The shop_quantity is set when
    the player said how many; it is 1 when they did not."""

    type: IntentType | None = None
    explore_direction: ExploreDirection | None = None
    unowned_weapons: list[str] = Field(default_factory=list)
    chest_side: ChestSide | None = None
    shop_item_name: ShopItemName | None = None
    shop_quantity: int | None = None

    def is_explore(self) -> bool:
        return self.type == "explore"

    def is_explore_forward(self) -> bool:
        return self.type == "explore" and self.explore_direction == "forward"

    def is_explore_left(self) -> bool:
        return self.type == "explore" and self.explore_direction == "left"

    def is_explore_right(self) -> bool:
        return self.type == "explore" and self.explore_direction == "right"

    def is_look(self) -> bool:
        return self.type == "look"

    def is_attack(self) -> bool:
        return self.type == "attack"

    def is_attack_with_missing_weapon(self) -> bool:
        return self.type == "attack" and bool(self.unowned_weapons)

    def is_shop(self) -> bool:
        return self.type == "shop"

    def get_shop_quantity(self) -> int:
        return 1 if self.shop_quantity is None else self.shop_quantity

    def is_drink_potion(self) -> bool:
        return self.type == "drink_potion"

    def is_cast_healing(self) -> bool:
        return self.type == "cast_healing"

    def is_open_chest(self) -> bool:
        return self.type == "open_chest"

    def is_open_left_chest(self) -> bool:
        return self.type == "open_chest" and self.chest_side == "left"

    def is_open_right_chest(self) -> bool:
        return self.type == "open_chest" and self.chest_side == "right"

    def is_multiple(self) -> bool:
        return self.type == "multiple"

    def is_unknown(self) -> bool:
        return self.type == "unknown"

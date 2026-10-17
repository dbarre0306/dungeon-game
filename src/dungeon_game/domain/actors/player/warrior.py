from typing import Literal, Self, cast

from pydantic import BaseModel

from dungeon_game.domain.actors.merchant.merchandise import Merchandise
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.intent import IntentType
from dungeon_game.domain.items.inventory_items import (
    BRONZE_SHIELD,
    BRONZE_SWORD,
    POTION,
    STEEL_SHIELD,
    STEEL_SWORD,
    InventoryItem,
    Shield,
    Sword,
)


class Potions(BaseModel):
    name: str = "Potions"
    quantity: int
    health_points: int


class Warrior(Player):
    type: Literal["warrior"] = "warrior"
    potions: Potions
    sword: Sword
    shield: Shield

    def get_facts(self) -> list[str]:
        return [
            "The player is a warrior.",
            f"The player has a {self.sword.name}.",
            f"The player has a {self.shield.name}.",
            f"The player's {self.shield.name} is {self.shield.state}.",
            f"The player has {self.gold_coins} gold coins.",
            f"The player has {self.potions.quantity} potion bottles.",
        ]

    def get_supported_intents(self) -> list[IntentType]:
        return [
            "explore",
            "look",
            "attack",
            "shop",
            "drink_potion",
            "open_chest",
        ]

    def get_supported_merchandise(self) -> list[Merchandise]:
        return [
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

    def with_purchased_item(
        self, item: InventoryItem, quantity: int, price: int
    ) -> Self:
        """Return a copy that spent `price` gold coins and added purchased item."""
        if item.type == "potion":
            return self._with_purchased_potions(quantity, price)
        elif item.type == "sword":
            sword = cast(Sword, item)
            return self._with_purchased_sword(sword, price)
        elif item.type == "shield":
            shield = cast(Shield, item)
            return self._with_purchased_shield(shield, price)
        raise Exception("invalid inventory item")

    def _with_purchased_potions(self, quantity: int, price: int) -> Self:
        potions = self.potions.model_copy(
            update={"quantity": self.potions.quantity + quantity}
        )
        return self.model_copy(
            update={"potions": potions, "gold_coins": self.gold_coins - price}
        )

    def _with_purchased_sword(self, sword: Sword, price: int) -> Self:
        return self.model_copy(
            update={"sword": sword, "gold_coins": self.gold_coins - price}
        )

    def _with_purchased_shield(self, shield: Shield, price: int) -> Self:
        return self.model_copy(
            update={"shield": shield, "gold_coins": self.gold_coins - price}
        )

    @property
    def offensive_weapon(self) -> str:
        return self.sword.name

    @property
    def additional_offensive_weapon_damage(self) -> int:
        return self.sword.additional_damage_points

    @property
    def defensive_weapon(self) -> str | None:
        if self.shield.condition == "broken":
            return None
        return self.shield.name

    @property
    def reduced_defensive_weapon_damage(self) -> int:
        return self.shield.block_points

    def with_defense_worn(self, absorbed: int) -> Self:
        return self.model_copy(update={"shield": self.shield.with_worn(absorbed)})

    def describe_defense_change(self, before: Self) -> str | None:
        if self.shield.condition == before.shield.condition:
            return None
        return f"The player's {self.shield.name} is now {self.shield.state}."

    def print(self):
        print(f"Gold Coins: {self.gold_coins}")
        print(f"Health Points: {self.health_points}")
        print(f"Is Fighting: {self.is_fighting}")
        print(f"Potions: {self.potions.quantity}")
        print(f"Sword: {self.sword.name}")
        print(
            f"Shield: {self.shield.name} "
            f"({self.shield.condition}:{self.shield.durability})"
        )


def create_default_warrior() -> Player:
    return Warrior(
        max_health_points=25,
        health_points=20,
        is_fighting=False,
        potions=Potions(health_points=8, quantity=2),
        sword=BRONZE_SWORD,
        shield=BRONZE_SHIELD,
        gold_coins=10,
        hit_bonus=3,
        current_room_index=0,
    )

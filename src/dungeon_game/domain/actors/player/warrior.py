from typing import Literal, Self, cast

from pydantic import BaseModel

from dungeon_game.domain.actors.player.inventory_items import (
    BRONZE_SHIELD,
    BRONZE_SWORD,
    InventoryItem,
    Shield,
    Sword,
)
from dungeon_game.domain.actors.player.player import Player


class Potions(BaseModel):
    name: str = "Potions"
    quantity: int
    health_points: int


class Warrior(Player):
    type: Literal["warrior"] = "warrior"
    potions: Potions
    sword: Sword
    shield: Shield

    def get_facts(self) -> str:
        return (
            f"The player is a warrior with a {self.sword.name} "
            f"and a {self.shield.name}."
        )
        # TODO: expand this: include potions and/or broken/damaged shield

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

    def get_weapon(self) -> str:
        return self.sword.name

    def get_extra_damage(self) -> int:
        return self.sword.additional_damage_points

    def get_defense(self) -> str | None:
        return self.shield.name

    def get_damage_reduction(self) -> int:
        return self.shield.defensive_health_points

    def print(self):
        print(f"Gold Coins: {self.gold_coins}")
        print(f"Health Points: {self.health_points}")
        print(f"Is Fighting: {self.is_fighting}")
        print(f"Potions: {self.potions.quantity}")
        print(f"Sword: {self.sword.name}")
        print(f"Shield: {self.shield.name}")


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

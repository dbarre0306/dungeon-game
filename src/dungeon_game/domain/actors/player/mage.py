from typing import Literal, Self

from pydantic import BaseModel

from dungeon_game.domain.actors.player.inventory_items import InventoryItem
from dungeon_game.domain.actors.player.player import Player


class FireBoltSpell(BaseModel):
    name: str
    additional_damage_points: int


class HealingSpell(BaseModel):
    name: str
    health_points: int
    quantity: int


class Staff(BaseModel):
    name: str
    fire_bolt_spell: FireBoltSpell
    healing_spell: HealingSpell


class Mage(Player):
    type: Literal["mage"] = "mage"
    staff: Staff

    def get_facts(self) -> list[str]:
        return [
            f"The player is a mage, a magical wizard.",
            f"The player has a {self.staff.name}.",
        ]

    def get_weapon(self) -> str:
        return self.staff.name

    def get_attack(self) -> str:
        return self.staff.fire_bolt_spell.name

    def get_extra_damage(self) -> int:
        return self.staff.fire_bolt_spell.additional_damage_points

    def with_purchased_item(
        self, item: InventoryItem, quantity: int, price: int
    ) -> Self:
        """Return a copy that spent `price` gold coins and added purchased item."""
        pass
        # TODO: implement

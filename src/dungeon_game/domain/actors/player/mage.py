from typing import Literal, Self

from pydantic import BaseModel

from dungeon_game.domain.actors.merchant.merchandise import Merchandise
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.intent import IntentType
from dungeon_game.domain.items.inventory_items import (
    ELDER_STAFF,
    InventoryItem,
)


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
            "The player is a mage, a magical wizard.",
            f"The player has a {self.staff.name}.",
        ]

    def get_supported_intents(self) -> list[IntentType]:
        return ["explore", "look", "attack", "shop", "open_chest"]

    def get_supported_merchandise(self) -> list[Merchandise]:
        return [
            Merchandise(
                type="elder_staff",
                name="elder staff",
                price=10,
                quantity=1,
                item=ELDER_STAFF,
            )
        ]

    @property
    def offensive_weapon(self) -> str:
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

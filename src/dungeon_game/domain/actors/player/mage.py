from typing import Literal, Self, cast

from dungeon_game.domain.actors.merchant.merchandise import Merchandise
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.intent import IntentType
from dungeon_game.domain.items.inventory_items import (
    ELDER_STAFF,
    STAFF,
    InventoryItem,
    Staff,
)


class Mage(Player):
    type: Literal["mage"] = "mage"
    staff: Staff

    def get_facts(self) -> list[str]:
        return [
            "The player is a mage, a magical wizard.",
            f"The player has a {self.staff.name} for casting spells.",
            f"The player can cast a fire bolt spell to attack an enemy.",
            f"The player has no defensive capabilities against an attack "
            "by an enemy.enemy.",
            f"The player can cast a healing spell to restore their health "
            "points to full strength.",
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

    @property
    def offensive_weapon_payload(self) -> str:
        return self.staff.fire_bolt_spell.name

    @property
    def additional_offensive_weapon_damage(self) -> int:
        return self.staff.fire_bolt_spell.additional_damage_points

    def with_purchased_item(
        self, item: InventoryItem, quantity: int, price: int
    ) -> Self:
        """Return a copy that spent `price` gold coins and added purchased item."""
        if item.type == "staff":
            return self._with_purchased_staff(cast(Staff, item), price)
        raise Exception("invalid inventory item")

    def _with_purchased_staff(self, staff: Staff, price: int) -> Self:
        return self.model_copy(
            update={"staff": staff, "gold_coins": self.gold_coins - price}
        )


def create_default_mage() -> Player:
    return Mage(
        max_health_points=25,
        health_points=20,
        is_fighting=False,
        staff=STAFF,
        gold_coins=10,
        hit_bonus=3,
        current_room_index=0,
    )

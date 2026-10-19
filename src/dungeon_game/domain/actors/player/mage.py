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
            *self._healing_facts(),
        ]

    def _healing_facts(self) -> list[str]:
        if self.healing_casts_left <= 0:
            return ["The player has no healing spell casts left."]
        return [
            "The player can cast a healing spell to restore their health "
            "points to full strength.",
            f"The player can cast the healing spell {self.healing_casts_left} "
            "more times.",
        ]

    def get_supported_intents(self) -> list[IntentType]:
        return ["explore", "look", "attack", "shop", "cast_healing", "open_chest"]

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
    def healing_casts_left(self) -> int:
        return self.staff.healing_spell.quantity

    def with_healed_by_healing_spell(self) -> Self:
        """Return a copy that spent one healing cast and is back at full health."""
        staff = self.staff.model_copy(
            update={"healing_spell": self.staff.healing_spell.with_cast()}
        )
        return self.model_copy(
            update={"staff": staff, "health_points": self.max_health_points}
        )

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
        """The new staff keeps the healing casts the old one had left."""
        carried = self.staff.healing_spell.quantity
        staff = staff.model_copy(
            update={"healing_spell": staff.healing_spell.with_added_casts(carried)}
        )
        return self.model_copy(
            update={"staff": staff, "gold_coins": self.gold_coins - price}
        )

    def print(self):
        print(f"Gold Coins: {self.gold_coins}")
        print(f"Health Points: {self.health_points}")
        print(f"Is Fighting: {self.is_fighting}")
        print(f"Staff: {self.staff.name}")
        print(f"Healing Spells: {self.healing_casts_left} ")


def create_default_mage() -> Player:
    return Mage(
        max_health_points=25,
        health_points=25,
        is_fighting=False,
        staff=STAFF,
        gold_coins=10,
        hit_bonus=3,
        current_room_index=0,
    )

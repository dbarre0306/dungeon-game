from typing import Literal

from dungeon_game.domain.intent import ChestSide, Intent
from dungeon_game.domain.rooms.combat_room import CombatRoom


class TreasureRoom(CombatRoom):
    """Two chests: one holds gold, the other a serpent. The player opens exactly
    one. The `enemy` is the serpent, who only fights once its chest is opened."""

    type: Literal["treasure_room"] = "treasure_room"
    serpent_side: ChestSide
    opened_side: ChestSide | None = None

    def is_serpent_loose(self) -> bool:
        """True while the player has opened the serpent's chest and not yet
        killed the serpent."""
        return self.opened_side == self.serpent_side and self.enemy.is_alive()

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_open_chest():
            return self._is_valid_open_chest(intent)
        if intent.is_explore():
            return self._is_valid_explore(intent)
        if intent.is_attack():
            return self._is_valid_attack()
        if intent.is_drink_potion():
            return (True, None)
        return (
            False,
            "Tell the player that you don't understand what they have asked.",
        )

    def _is_valid_open_chest(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.chest_side is None:
            return (
                False,
                "Tell the player that they must say which chest to open, "
                "the left chest or the right chest.",
            )
        if self.opened_side is None:
            return (True, None)
        return (
            False,
            "Tell the player that they have already opened a chest and "
            "cannot open the other one.",
        )

    def _is_valid_explore(self, intent: Intent) -> tuple[bool, str | None]:
        if not intent.is_explore_forward():
            return (
                False,
                (
                    "Tell the player that the only way out is forward through "
                    "the passageway."
                ),
            )
        if self.opened_side is None:
            return (
                False,
                "Tell the player that they must open one of the chests "
                "before they leave.",
            )
        if self.is_serpent_loose():
            return (
                False,
                "Tell the player that the serpent blocks the way out and they "
                "must kill it before they can leave. Tell them they lost "
                "their turn trying to leave.",
            )
        return (True, None)

    def _is_valid_attack(self) -> tuple[bool, str | None]:
        if self.is_serpent_loose():
            return (True, None)
        if self.enemy.is_dead():
            return (
                False,
                "Tell the player that the serpent is already dead "
                "and they can stop attacking.",
            )
        return (False, "Tell the player that there is nothing here to attack.")

    def get_room_facts(self) -> list[str]:
        if self.opened_side is None:
            return [
                "There are two identical chests, one to the left and the other "
                "to the right of the passageway.",
                "One chest contains gold coins and the other contains a serpent.",
                "There is only one passageway out of this room.",
                "The player has not opened a chest yet and must open one "
                "before leaving.",
            ]
        other_side = "right" if self.opened_side == "left" else "left"
        chests = (
            f"There are two chests: the {self.opened_side} chest is open "
            f"and the {other_side} chest is closed."
        )
        passageway = "There is only one passageway out of this room."
        if self.opened_side != self.serpent_side:
            return [
                chests,
                "The open chest contained gold coins, which the player collected.",
                passageway,
                "The way forward is clear.",
            ]
        if self.is_serpent_loose():
            return [
                chests,
                "A live serpent came out of the open chest and is attacking "
                "the player.",
                passageway,
                "The player must kill the serpent before they can leave.",
            ]
        return [
            chests,
            "The serpent that came out of the open chest is dead.",
            passageway,
            "The way forward is clear.",
        ]

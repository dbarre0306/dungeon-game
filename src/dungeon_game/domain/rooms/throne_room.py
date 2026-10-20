from typing import Literal

from dungeon_game.domain.intent import Intent, IntentType
from dungeon_game.domain.rooms.combat_room import NONEXISTENT_WEAPON_REFUSAL, CombatRoom


class ThroneRoom(CombatRoom):
    """The last room: there is no way out. The `enemy` is the troll, and killing
    it wins the game."""

    type: Literal["throne_room"] = "throne_room"

    def _is_valid_room_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_explore():
            return (
                False,
                (
                    "Tell the player that there is no way out of this room; "
                    f"the only thing left to do is to defeat the {self.enemy.name}."
                ),
            )
        if intent.is_attack():
            if self.enemy.is_dead():
                return (
                    False,
                    f"Tell the player that the {self.enemy.name} is already dead "
                    "and they can stop attacking.",
                )
            if intent.is_attack_with_nonexistent_weapon():
                return (False, NONEXISTENT_WEAPON_REFUSAL)
            return (True, None)
        return (
            False,
            "Tell the player that you don't understand what they have asked.",
        )

    def _legal_room_intents(self) -> frozenset[IntentType]:
        return frozenset({"explore", "attack"})

    def get_room_facts(self) -> list[str]:
        if self.enemy.is_dead():
            return [
                f"The {self.enemy.name} lies dead beside its stone throne.",
                "There is no way out of this room.",
            ]
        return [
            f"There is a {self.enemy.name} twice the player's size sitting on a "
            "stone throne.",
            f"The {self.enemy.name} has a {self.enemy.offensive_weapon}.",
            f"The {self.enemy.name} has the Amulet of Valdorin around its neck.",
            "There is no way out of this room.",
        ]

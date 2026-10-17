from typing import Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.combat_room import CombatRoom

_NUMBER_OF_GOLD_COINS = 5


class MonsterRoom(CombatRoom):
    type: Literal["monster_room"] = "monster_room"
    gold_coins: int = _NUMBER_OF_GOLD_COINS

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_explore():
            if self.enemy.is_alive():
                return (
                    False,
                    (
                        f"Tell the player that the {self.enemy.name} "
                        "will not let them pass."
                    ),
                )
            elif intent.is_explore_forward():
                return (True, None)
            else:
                return (
                    False,
                    (
                        "Tell the player that the only way out is forward through "
                        "the passageway."
                    ),
                )
        elif intent.is_attack():
            if self.enemy.is_alive():
                return (True, None)
            return (
                False,
                (
                    f"Tell the player that the {self.enemy.name} is already dead "
                    "and they can stop attacking."
                ),
            )
        elif intent.is_drink_potion():
            return (True, None)
        return (
            False,
            "Tell the player that you don't understand what they have asked.",
        )

    def get_room_facts(self) -> list[str]:
        return [
            f"The {self.enemy.name}, armed with {self.enemy.get_weapon()}, "
            "is in this room and is itching for a fight.",
            "The player cannot go back the way they came.",
            "There is only one exit, doorway, or passageway to the next room.",
            *self._gold_facts(),
        ]

    def _gold_facts(self) -> list[str]:
        if self.gold_coins == 0:
            return ["The player has collected the gold coins; none remain here."]
        return [f"There are {self.gold_coins} gold coins behind the {self.enemy.name}."]

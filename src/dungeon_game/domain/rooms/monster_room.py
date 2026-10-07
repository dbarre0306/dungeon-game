from typing import Literal

from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.combat_room import CombatRoom

_NUMBER_OF_GOLD_COINS = 5


class MonsterRoom(CombatRoom):
    type: Literal["monster_room"] = "monster_room"
    gold_coins: int = _NUMBER_OF_GOLD_COINS

    def __init__(self, enemy: Enemy):
        super().__init__(enemy=enemy)

    def is_valid_action(self, action: Intent) -> tuple[bool, str | None]:
        if action.type == "explore":
            if self.enemy.is_alive():
                return (
                    False,
                    (
                        f"Tell the player that the {self.enemy.name} "
                        "will not let them pass."
                    ),
                )
            elif self._is_forward(action):
                return (True, None)
            else:
                return (
                    False,
                    "Tell the player that the only way out is forward through the passageway.",
                )
        elif action.type == "attack":
            if self.enemy.is_alive():
                return (True, None)
            return (
                False,
                f"Tell the player that the {self.enemy.name} is already dead and they can stop attacking.",
            )
        elif action.type == "drink_potion":
            return (True, None)
        return (
            False,
            "Tell the player that you don't understand what they have asked.",
        )

    def _is_forward(self, action: Intent) -> bool:
        return action.explore_direction == "forward" or action.explore_direction is None

    def get_room_facts(self) -> list[str]:
        return [
            f"The {self.enemy.name}, armed with {self.enemy.get_weapon()}, "
            "is in this room and is itching for a fight.",
            "The player cannot go back the way they came.",
            "There is only one exit, doorway, or passageway to the next room.",
            f"There are {_NUMBER_OF_GOLD_COINS} gold coins "
            f"behind the {self.enemy.name}.",
        ]

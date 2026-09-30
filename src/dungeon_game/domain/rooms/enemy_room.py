from typing import Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.npc.enemy import Enemy
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

_NUMBER_OF_GOLD_COINS = 5


class EnemyRoom(DungeonRoom):
    type: Literal["enemy_room"] = "enemy_room"
    enemy: Enemy
    gold_coins: int = _NUMBER_OF_GOLD_COINS

    def __init__(self, enemy: Enemy):
        super().__init__(enemy=enemy)

    def is_valid_action(self, action: Intent) -> tuple[bool, str | None]:
        if action.type == "explore" and self.enemy.is_alive():
            return (False, f"The {self.enemy.name} will not let you pass.")
        # elif action.type == "get_coins":
        elif action.type == "attack":
            if self.enemy.is_alive():
                return (True, None)
            return (False, f"The {self.enemy.name} is already dead. You can stop now.")
        elif action.type == "drink_potion":
            return (True, None)
        return (False, "I have no idea what you trying to do.")

    def get_initial_facts(self) -> list[str]:
        return [
            f"An {self.enemy.description} is in this room and he's itching for a fight.",
            "The player cannot go back the way they came.",
            "There is only one exit, doorway, or passageway to the next room.",
            f"There are {_NUMBER_OF_GOLD_COINS} gold coins behind the {self.enemy.name}.",
        ]

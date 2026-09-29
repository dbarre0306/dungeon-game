from typing import Literal

from pydantic import BaseModel

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

_NUMBER_OF_GOLD_COINS = 5


class Enemy(BaseModel):
    name: str
    description: str
    health_points: int

    def __init__(self, name, description, health_points):
        super().__init__(
            name=name, description=description, health_points=health_points
        )


class EnemyRoom(DungeonRoom):
    type: Literal["enemy_room"] = "enemy_room"
    enemy: Enemy
    gold_coins: int = _NUMBER_OF_GOLD_COINS

    def __init__(self, enemy: Enemy):
        super().__init__(enemy=enemy)

    def is_valid_action(self, action: Intent) -> tuple[bool, str | None]:
        if action.type == "explore" and self.enemy.health_points > 0:
            return (False, f"The {self.enemy.name} will not let you pass.")
        # elif action.type == "get_coins":
        elif action.type == "combat":
            return (True, None)
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

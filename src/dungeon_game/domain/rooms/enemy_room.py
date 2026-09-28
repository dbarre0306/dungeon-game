from typing import Literal

from dungeon_game.domain.misc.action import Action
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class EnemyRoom(DungeonRoom):
    type: Literal["enemy_room"] = "enemy_room"
    enemy: str

    def is_valid_action(self, action: Action) -> tuple[bool, str | None]:
        return (True, None)

    def get_initial_facts(self) -> list[str]:
        return [f"An {self.enemy} is in this room and he's itching for a fight."]

from typing import Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class CaveChamber(DungeonRoom):
    type: Literal["cave_chamber"] = "cave_chamber"

    def is_valid_action(self, action: Intent) -> tuple[bool, str | None]:
        if action.explore_option == "look":
            return (True, None)
        elif action.explore_option == "left":
            return (True, None)
        elif action.explore_option == "right":
            return (True, None)
        return False, "You must go either left or right."

    def get_initial_facts(self) -> list[str]:
        return [
            "The player is in the cave chamber.",
            "The chamber has a passageway to the left and another the right.",
            "There is a flicking torch on the wall.",
            "There may be silence or noises coming from either passageway.",
        ]

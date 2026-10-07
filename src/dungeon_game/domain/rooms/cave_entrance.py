# The Cave Entrance is not "room" in the real world, but
# it does simplify the software design.
from typing import Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class CaveEntrance(DungeonRoom):
    type: Literal["cave_entrance"] = "cave_entrance"

    def is_valid_action(self, action: Intent) -> tuple[bool, str | None]:
        if action.explore_direction == "forward":
            return (True, None)
        return False, (
            "Tell the player that they cannot go that way "
            "and that they must enter the cave."
        )

    def get_room_facts(self) -> list[str]:
        return [
            "The player is standing at the entrance of the cave.",
            "The cave entrance is directly in front of the player.",
        ]

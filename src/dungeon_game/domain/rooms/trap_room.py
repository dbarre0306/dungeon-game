from typing import Literal

from dungeon_game.domain.misc.action import Action
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class TrapRoom(DungeonRoom):
    type: Literal["trap_room"] = "trap_room"

    def is_valid_action(self, action: Action) -> tuple[bool, str | None]:
        return (True, None)

    def get_initial_facts(self) -> list[str]:
        return [
            "There are gold coins on the other side of the room.",
            "There is only one passageway forward.",
        ]

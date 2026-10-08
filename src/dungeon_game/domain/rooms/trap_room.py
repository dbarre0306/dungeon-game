from typing import Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class TrapRoom(DungeonRoom):
    type: Literal["trap_room"] = "trap_room"
    trap_type: str

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        return (True, None)

    def get_room_facts(self) -> list[str]:
        return [
            "There are gold coins on the other side of the room.",
            "There is only one passageway forward.",
        ]

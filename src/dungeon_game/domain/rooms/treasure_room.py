from typing import Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class TreasureRoom(DungeonRoom):
    type: Literal["treasure_room"] = "treasure_room"

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        return (True, None)

    def get_room_facts(self) -> list[str]:
        return [
            "There are two identical chests to the left and right.",
            "One chest contains gold coins.",
            "The other chest contains a serpent.",
            "There is only one passageway out of this room.",
        ]

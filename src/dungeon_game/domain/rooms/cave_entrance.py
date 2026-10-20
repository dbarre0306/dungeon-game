# The Cave Entrance is not "room" in the real world, but
# it does simplify the software design.
from typing import Literal

from dungeon_game.domain.intent import Intent, IntentType
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class CaveEntrance(DungeonRoom):
    type: Literal["cave_entrance"] = "cave_entrance"

    def _is_valid_room_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_explore_forward():
            return (True, None)
        return False, (
            "Tell the player that they cannot go that way "
            "and that they must enter the cave."
        )

    def _legal_room_intents(self) -> frozenset[IntentType]:
        return frozenset({"explore"})

    def get_room_facts(self) -> list[str]:
        return [
            "The player is standing at the entrance of the cave.",
            "The cave entrance is directly in front of the player.",
        ]

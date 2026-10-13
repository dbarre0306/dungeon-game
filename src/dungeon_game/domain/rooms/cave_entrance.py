# The Cave Entrance is not "room" in the real world, but
# it does simplify the software design.
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

if TYPE_CHECKING:
    from dungeon_game.game_state import GameState


class CaveEntrance(DungeonRoom):
    type: Literal["cave_entrance"] = "cave_entrance"

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_explore_forward():
            return (True, None)
        return False, (
            "Tell the player that they cannot go that way "
            "and that they must enter the cave."
        )

    def get_room_facts(self, state: GameState) -> list[str]:
        return [
            "The player is standing at the entrance of the cave.",
            "The cave entrance is directly in front of the player.",
        ]

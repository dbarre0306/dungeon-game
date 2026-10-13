from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

if TYPE_CHECKING:
    from dungeon_game.game_state import GameState


class CaveChamber(DungeonRoom):
    type: Literal["cave_chamber"] = "cave_chamber"

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_look():
            return (True, None)
        elif intent.is_explore_left():
            return (True, None)
        elif intent.is_explore_right():
            return (True, None)
        return False, "Tell the player they must go either left or right."

    def get_room_facts(self, state: GameState) -> list[str]:
        return [
            "The player is in the cave chamber.",
            "The chamber has a passageway to the left and another the right.",
            "There is a flicking torch on the wall.",
            "There may be silence or noises coming from either passageway.",
        ]

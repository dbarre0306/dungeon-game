from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

if TYPE_CHECKING:
    from dungeon_game.game_state import GameState


class ThroneRoom(DungeonRoom):
    type: Literal["throne_room"] = "throne_room"

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        return (True, None)

    def get_room_facts(self, state: GameState) -> list[str]:
        return [
            "There is a troll twice the player's size sitting on a stone throne.",
            "The troll has a large spiked wooden club.",
            "The troll has the Amulet of Valdorin around his neck.",
        ]

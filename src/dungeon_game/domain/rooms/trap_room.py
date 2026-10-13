from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

if TYPE_CHECKING:
    from dungeon_game.game_state import GameState


class TrapRoom(DungeonRoom):
    type: Literal["trap_room"] = "trap_room"
    trap_type: str
    is_sprung: bool = False

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_explore():
            if intent.is_explore_forward():
                return (True, None)
            return (
                False,
                (
                    "Tell the player that the only way out is forward through "
                    "the passageway."
                ),
            )
        elif intent.is_drink_potion():
            return (True, None)
        return (
            False,
            "Tell the player that you don't understand what they have asked.",
        )

    def get_room_facts(self, state: GameState) -> list[str]:
        if self.is_sprung:
            return [
                "The player has crossed the room and the trap has been sprung.",
                "The player has collected all of the gold coins; "
                "no gold remains in the room.",
                "The way forward is clear.",
                "There is only one passageway forward.",
            ]
        return [
            "There are gold coins on the other side of the room.",
            "There is only one passageway forward, also on the other side.",
        ]

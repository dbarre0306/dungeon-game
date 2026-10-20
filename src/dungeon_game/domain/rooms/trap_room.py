from typing import Literal

from dungeon_game.domain.intent import Intent, IntentType
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class TrapRoom(DungeonRoom):
    type: Literal["trap_room"] = "trap_room"
    trap_type: str
    is_sprung: bool = False

    def _is_valid_room_intent(self, intent: Intent) -> tuple[bool, str | None]:
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
        return (
            False,
            "Tell the player that you don't understand what they have asked.",
        )

    def _legal_room_intents(self) -> frozenset[IntentType]:
        return frozenset({"explore"})

    def get_room_facts(self) -> list[str]:
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

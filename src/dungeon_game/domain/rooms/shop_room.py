from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

if TYPE_CHECKING:
    from dungeon_game.game_state import GameState


class ShopRoom(DungeonRoom):
    type: Literal["shop_room"] = "shop_room"

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        return (True, None)

    def get_room_facts(self, state: GameState) -> list[str]:
        return [
            "There is a merchant selling stuff.",
            "There is only one passageway forward.",
        ]

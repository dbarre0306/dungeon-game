from typing import Literal

from dungeon_game.domain.misc.action import Action
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class ShopRoom(DungeonRoom):
    type: Literal["shop_room"] = "shop_room"

    def is_valid_action(self, action: Action) -> tuple[bool, str | None]:
        return (True, None)

    def get_initial_facts(self) -> list[str]:
        return [
            "There is a merchant selling stuff.",
            "There is only one passageway forward.",
        ]

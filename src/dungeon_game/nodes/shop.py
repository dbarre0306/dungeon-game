from typing import Any

from dungeon_game.game_state import GameState


class ShopNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        return {"narration": ["shop"]}

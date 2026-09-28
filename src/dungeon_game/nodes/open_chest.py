from typing import Any

from dungeon_game.game_state import GameState


class OpenChestNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        return {"narration": "open_chest"}

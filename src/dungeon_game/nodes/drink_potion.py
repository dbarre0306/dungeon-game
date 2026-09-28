from typing import Any

from dungeon_game.game_state import GameState


class DrinkPotionNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        return {"narration": "drink_potion"}

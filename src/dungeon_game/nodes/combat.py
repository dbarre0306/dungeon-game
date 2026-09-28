from typing import Any

from dungeon_game.game_state import GameState


class CombatNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        return {"narration": "combat"}

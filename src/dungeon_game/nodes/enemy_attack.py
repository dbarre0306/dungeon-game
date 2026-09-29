from typing import Any

from dungeon_game.game_state import GameState


class EnemyAttackNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        return {"narration": "enemy attack"}

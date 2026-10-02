from typing import Any

from dungeon_game.game_state import GameState


class EnemyAttackNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        narration = state.narration + ["The enemy has struck back."]
        return {"narration": narration}


# include room events (probably the last event which
# corresponds to whether the enemy was hit or not)
# NOTE: other things like drinking a potion could have happened.

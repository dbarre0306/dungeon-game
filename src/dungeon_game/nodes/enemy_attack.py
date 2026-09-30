from typing import Any

from dungeon_game.game_state import GameState


class EnemyAttackNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        return {"narration": f"{state.narration} The enemy has struck back."}


# include room events (probably the last event which
# corresponds to whether the enemy was hit or not)
# NOTE: other things like drinking a potion could have happened.

from dungeon_game.game_state import GameState


class CombatNode:

    def execute(self, state: GameState) -> GameState:
        return {"narration": "combat"}

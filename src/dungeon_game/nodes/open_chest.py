from dungeon_game.game_state import GameState


class OpenChestNode:

    def execute(self, state: GameState) -> GameState:
        return {"narration": "open_chest"}

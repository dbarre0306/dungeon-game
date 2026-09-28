from dungeon_game.game_state import GameState


class ShopNode:

    def execute(self, state: GameState) -> GameState:
        return {"narration": "shop"}

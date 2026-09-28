from dungeon_game.game_state import GameState


class DrinkPotionNode:

    def execute(self, state: GameState) -> GameState:
        return {"narration": "drink_potion"}

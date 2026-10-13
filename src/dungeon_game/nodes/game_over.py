from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.game_state import GameState


class GameOverNode:
    """Ends the game when the player is dead, with a closing word from the
    dungeon master."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("GAME OVER CHECK")
        # TODO: the game is also over once the player retrieves the amulet
        if state.player.is_alive():
            return {}
        response = self._dungeon_master_agent.invoke(
            state,
            "The player has died and the game is over. "
            "Write a brief, final farewell to the player. "
            "Do NOT repeat how the player died.",
        )
        return {
            "narration": state.narration + [response.narration],
            "game_over": True,
        }

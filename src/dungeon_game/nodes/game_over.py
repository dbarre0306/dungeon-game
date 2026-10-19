from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.game_state import GameState


class GameOverNode:
    """Ends the game when the player is dead, or has killed the troll and taken
    the amulet, with a closing word from the dungeon master."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("GAME OVER CHECK")
        if state.player.is_dead():
            return self._defeat(state)
        if self._has_killed_the_troll(state):
            return self._victory(state)
        return {}

    @staticmethod
    def _has_killed_the_troll(state: GameState) -> bool:
        room = state.get_current_room()
        return isinstance(room, ThroneRoom) and room.enemy.is_dead()

    def _defeat(self, state: GameState) -> dict[str, Any]:
        return self._end_game(
            state,
            "The player has died and the game is over. "
            "Write a brief, final farewell to the player. "
            "Do NOT repeat how the player died.",
        )

    def _victory(self, state: GameState) -> dict[str, Any]:
        return self._end_game(
            state,
            "The player has killed the troll and taken the Amulet of Valdorin "
            "from its neck. Tell the player that they took the amulet from the "
            "troll's neck, then that the amulet's power brings them back to the "
            "kingdom, and write a brief victory narration to end the game.",
        )

    def _end_game(self, state: GameState, msg: str) -> dict[str, Any]:
        response = self._dungeon_master_agent.invoke(state, msg)
        return {
            "narration": state.narration + [response.narration],
            "game_over": True,
        }

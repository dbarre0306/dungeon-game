from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.game_state import GameState


class OpenChestNode:
    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("OPEN CHEST")
        room = state.get_current_room()
        is_valid, msg = room.is_valid_intent(state.intent)
        if is_valid:
            return {}
        response = self._dungeon_master_agent.invoke(room, state.player, msg)
        return {"narration": [response.narration]}

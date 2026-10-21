from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.arrival import describe_arrival


class ExploreNode:
    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        room = state.get_current_room()
        is_valid, msg = room.is_valid_intent(state.intent)
        if not is_valid:
            response = self._dungeon_master_agent.invoke(
                state, msg, include_command=True
            )
            return {"narration": [response.narration], "attempt_failed": True}

        next_room = state.get_next_room()
        if next_room is None:
            return {"narration": ["There is nowhere further to go."]}

        next_room_index = state.player.current_room_index + 1
        player_update: dict[str, Any] = {"current_room_index": next_room_index}
        if isinstance(next_room, MonsterRoom | ThroneRoom):
            player_update["is_fighting"] = True
        player = state.player.model_copy(update=player_update)
        description = self._get_room_description(
            state.model_copy(update={"player": player})
        )
        new_dungeon = state.dungeon.with_room_updated(
            next_room_index, history=[description]
        )
        return {
            "narration": [description],
            "player": player,
            "dungeon": new_dungeon,
        }

    def _get_room_description(self, state: GameState) -> str:
        return describe_arrival(self._dungeon_master_agent, state, include_command=True)

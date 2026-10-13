from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.game_state import GameState


class LookNode:
    """Look is valid in every room.  A player should always be able to
    look around and see what is in a room.  Therefore, there is no reason to
    validate it."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("LOOK")
        room = state.get_current_room()
        if len(room.history) == 0:
            description = self._get_room_description_on_entry(state)
            new_dungeon = state.dungeon.with_room_updated(
                state.player.current_room_index, history=[description]
            )
            return {"narration": [description], "dungeon": new_dungeon}
        else:
            description = self._get_room_description(state)
            return {"narration": [description]}

    def _get_room_description_on_entry(self, state: GameState) -> str:
        msg = (
            "Describe the room to the player using only the room facts. "
            "The player "
            "needs to clearly understand what is there in order to make a decision "
            "on what to do next.  Do not invent new "
            "rooms, paths, exits, creatures, or other plot details that are "
            "not listed. If the facts or room history don't mention something, "
            "leave it out."
        )
        return self._dungeon_master_agent.invoke(state, msg).narration

    def _get_room_description(self, state: GameState) -> str:
        msg = (
            "Tell the player what is in the room.  Keep it simple. "
            "Do NOT describe the walls, ground, floor, or ceiling. "
            "Do NOT tell the player what they can smell, taste, or hear. "
            "Do NOT make things up. "
            "You can only give a list based on the room facts and the room history. "
            "Stick to what is in the room. "
            "Keep it to one sentence. "
            "BE BORING!"
        )
        return self._dungeon_master_agent.invoke(state, msg).narration

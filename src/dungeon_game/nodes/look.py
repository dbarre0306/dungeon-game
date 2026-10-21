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
        return {"narration": [self._get_room_description(state)]}

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
        return self._dungeon_master_agent.invoke(
            state, msg, include_command=True
        ).narration

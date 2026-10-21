from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.game_state import GameState
from dungeon_game.nodes.arrival import describe_arrival


class IntroNode:
    """Opens the game: tells the player their quest and describes the room they
    start in.  It runs once, before the player has typed anything."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        description = describe_arrival(
            self._dungeon_master_agent,
            state,
            preamble=(
                "This is the opening of the game.  Begin with one sentence "
                "telling the player that their quest is to retrieve the Amulet "
                "of Valdorin from the troll that stole it.  For the rest of "
                "the narration, follow these instructions:  "
            ),
        )
        new_dungeon = state.dungeon.with_room_updated(
            state.player.current_room_index, history=[description]
        )
        return {
            "narration": [description],
            "dungeon": new_dungeon,
            "opening": False,
        }

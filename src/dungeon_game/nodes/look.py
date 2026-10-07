from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.game_state import GameState


class LookNode:
    """Look is valid in every room.  A player should always be able to
    look around and see what is in a room.  Therefore, there is no reason to
    validate it."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("LOOK !!!!")
        room = state.get_current_room()
        if len(room.history) == 0:
            print("--- generate a new description")
            description = self._get_room_description_on_entry(room, state.player)
            new_dungeon = state.dungeon.with_room_updated(
                state.player.current_room_index, history=[description]
            )
            return {"narration": [description], "dungeon": new_dungeon}
        else:
            print("--- generate a simple looking around the room description")
            description = self._get_room_description(room, state.player)
            return {"narration": [description]}

    def _get_room_description_on_entry(self, room: DungeonRoom, player: Player) -> str:
        msg = (
            "Describe the room to the player using only the room facts "
            "The player "
            "needs to clearly understand what is there in order to make a decision "
            "on what do to next.  Do not invent new "
            "rooms, paths, exits, creatures, or other plot details that are "
            "not listed. If the facts or room history don't mention something, "
            "leave it out."
        )
        return self._dungeon_master_agent.invoke(room, player, msg).narration

    def _get_room_description(self, room: DungeonRoom, player: Player) -> str:
        msg = (
            "Tell the player what is in the room.  Keep it simple. "
            "Do NOT describe the walls, ground, floor, or ceiling. "
            "Do NOT tell the player what they can smell, taste, or hear. "
            "Do NOT make things up. "
            "You can only give a list based on the room facts and the narration "
            "that has occurred in that room. "
            "Stick to what is in the room. "
            "Keep it to one sentence."
            "BE BORING!"
        )
        return self._dungeon_master_agent.invoke(room, player, msg).narration

    @staticmethod
    def _format_list(items: list[str]) -> str:
        return "\n".join(map(lambda f: f"- {f}", items))

    def _initial_room_description(self, room: DungeonRoom) -> str:
        if room.room_description is None:
            return ""
        return (
            "This is the initial description of the room: "
            f"\n{room.room_description} "
            "\n\nDon't repeat this initial description.  Just give a "
            "simple list of what the player would be seeing. "
            "Do not describe the walls, ground, floor, or ceiling. "
            "Do NOT tell the player what they can smell, taste, or hear.  "
            "Stick to what is in the room. "
            "BE BORING!"
        )

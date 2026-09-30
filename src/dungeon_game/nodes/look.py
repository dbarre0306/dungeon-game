from typing import Any

from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.game_state import GameState


class LookNode:

    def __init__(self, dungeon_master_agent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("LOOK !!!!")
        room_index = state.player.current_room_index
        room = state.get_current_room()
        if room.room_description is None:
            print("--- generate a new description")
            description = self._get_room_description_on_entry(room)
            new_dungeon = state.dungeon.with_room_updated(
                room_index, room_description=description
            )
            return {"narration": description, "dungeon": new_dungeon}
        else:
            print("--- generate a simple looking around the room description")
            description = self._get_room_description(room)
            return {"narration": description}

    def _get_room_description_on_entry(self, room: DungeonRoom) -> str:
        msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "Describe the room to the player using only the initial facts "
                    "as well as the events that have occurred. Do not be overdramatic. The player "
                    "needs to clearly understand what is there in order to make a decison on what "
                    "do to next.  Try to keep it to a few sentences or less. Do not invent new "
                    "rooms, paths, exits, creatures, or other plot details that are not listed "
                    "below — if the facts and events don't mention something, leave it out."
                    "\n\nThe initial facts are: "
                    f"{self._format_list(room.get_initial_facts())}"
                    f"\n\nThe events are: "
                    f"{self._format_list(room.events)}",
                }
            ]
        }
        result = self._dungeon_master_agent.invoke(msg)
        response = result["structured_response"]
        return response.narration

    def _get_room_description(self, room: DungeonRoom) -> str:
        msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "Tell the player what is in the room.  Keep it simple. "
                    "Do NOT describe the walls, ground, floor, or ceiling. "
                    "Do NOT tell the player what they can smell, taste, or hear. "
                    "Do NOT make things up. "
                    "You can only give a list of based on the inital description, the "
                    "initial facts, and the events."
                    "Stick to what is in the room. "
                    "Keep it to one sentence."
                    "BE BORING!"
                    "\n\nInitial description of the room: "
                    f"\n\n{room.room_description}"
                    "\n\nThe initial facts are: "
                    f"{self._format_list(room.get_initial_facts())}"
                    f"\n\nThe events are: "
                    f"{self._format_list(room.events)}",
                }
            ]
        }
        result = self._dungeon_master_agent.invoke(msg)
        response = result["structured_response"]
        return response.narration

    @staticmethod
    def _format_list(items: list[str]) -> str:
        return "\n".join(map(lambda f: f"- {f}", items))

    def _initial_room_description(self, room: DungeonRoom) -> str:
        if room.room_description == None:
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

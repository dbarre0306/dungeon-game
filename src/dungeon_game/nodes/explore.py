from typing import Any

from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.game_state import GameState


class ExploreNode:

    def __init__(self, dungeon_master_agent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        room = self.get_room(state)
        is_valid, err_msg = room.is_valid_action(state.action)
        if is_valid:
            return self._explore_cave_entrance(state)
        else:
            return {"narration": err_msg}

    def _explore_cave_entrance(self, state: GameState) -> dict[str, Any]:
        if state.action.explore_option == "look":
            return self._describe_room(state)
        else:
            return self._go_to_next_room_and_describe(state)

    def _describe_room(self, state: GameState) -> dict[str, Any]:
        room = self.get_room(state)
        narration = self._get_room_description(room)
        return {"narration": narration}

    def _go_to_next_room_and_describe(self, state: GameState) -> dict[str, Any]:
        next_room = self.get_next_room(state)
        if next_room is None:
            return {"narration": "There is nowhere further to go."}
        narration = self._get_room_description(next_room)
        player = state.player.model_copy(
            update={"current_room_index": state.player.current_room_index + 1}
        )
        return {"narration": narration, "player": player}

    def get_room(self, state: GameState) -> DungeonRoom:
        return state.dungeon.get_room(state.player.current_room_index)

    def get_next_room(self, state: GameState) -> DungeonRoom | None:
        return state.dungeon.get_next_room(state.player.current_room_index)

    def _get_room_description(self, room: DungeonRoom) -> str:
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

    @staticmethod
    def _format_list(items: list[str]) -> str:
        return "\n".join(map(lambda f: f"- {f}", items))

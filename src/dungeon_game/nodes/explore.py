from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.game_state import GameState


class ExploreNode:

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print(f"EXPLORE : {state.intent.explore_direction}")
        next_room = state.get_next_room()
        if next_room is None:
            return {"narration": ["There is nowhere further to go."]}

        room = state.get_current_room()
        is_valid, err_msg = room.is_valid_action(state.intent)
        if is_valid:
            next_room_index = state.player.current_room_index + 1
            description = self._get_room_description(next_room)
            player = state.player.model_copy(
                update={"current_room_index": next_room_index}
            )
            new_dungeon = state.dungeon.with_room_updated(
                next_room_index, room_description=description
            )
            return {
                "narration": [description],
                "player": player,
                "dungeon": new_dungeon,
            }
        else:
            return {"narration": [err_msg]}

    def _get_room_description(self, room: DungeonRoom) -> str:
        msg = (
            "Describe the room to the player using only the initial facts "
            "as well as the events that have occurred. Do not be overdramatic. The player "
            "needs to clearly understand what is there in order to make a decison on what "
            "do to next.  Try to keep it to a few sentences or less. Do not invent new "
            "rooms, paths, exits, creatures, or other plot details that are not listed "
            "below — if the facts and events don't mention something, leave it out."
            "\n\nThe initial facts are:\n"
            f"{self._format_list(room.get_initial_facts())}"
            f"\n\nThe events are:\n"
            f"{self._format_list(room.events)}"
        )
        return self._dungeon_master_agent.invoke(msg).narration

    @staticmethod
    def _format_list(items: list[str]) -> str:
        return "\n".join(map(lambda f: f"- {f}", items))

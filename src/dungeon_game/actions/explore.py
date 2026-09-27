from dungeon_game.game_state import DungeonRoom, GameState
from dungeon_game.rooms.room_factory import create_room


class ExploreNode:

    def __init__(self, dungeon_master_agent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> GameState:
        room = create_room(state["current_room"])
        is_valid, err_msg = room.is_valid_action(state["action"])
        if is_valid:
            return self._explore_cave_entrance(state)
        else:
            return {"narration": err_msg}

    def _explore_cave_entrance(self, state: GameState) -> GameState:
        if state["action"]["explore_option"] == "look":
            return self._describe_room(state)
        else:
            return self._go_to_next_room_and_describe(state)

    def _describe_room(self, state: GameState):
        room = state["current_room"]
        narration = self._get_room_description(room)
        return {"narration": narration}

    def _go_to_next_room_and_describe(self, state: GameState):
        next_room = state["current_room"]["next_room"]
        narration = self._get_room_description(next_room)
        return {"narration": narration, "current_room": next_room}

    def _get_room_description(self, room: DungeonRoom) -> GameState:
        msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "Describe the room to the player using only the initial facts "
                    "as well as the events that have occurred. Do not be overdramatic. The player "
                    "needs to clearly understand what is there in order to make a decison on what "
                    "do to next.  Try to keep it to a few sentences or less."
                    "\n\nThe initial facts are: "
                    f"{self._format_list(room["initial_facts"])}"
                    f"\n\nThe events are: "
                    f"{self._format_list(room["events"])}",
                }
            ]
        }
        result = self._dungeon_master_agent.invoke(msg)
        response = result["structured_response"]
        return response.narration

    @staticmethod
    def _format_list(items: list[str]) -> str:
        return "\n".join(map(lambda f: f"- {f}", items))

import os
import pprint
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from dungeon_game.game_state import DungeonRoom, GameState

load_dotenv()

ActionType = Literal[
    "explore", "combat", "shop", "drink_potion", "open_chest", "multiple", "unknown"
]
ExploreOption = Literal["left", "right", "forward", "backward", "look"]


class ExploreNode:

    def __init__(self, dungeon_master_agent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> GameState:
        pprint.pprint(f"Explore Room: {state["current_room"]["id"]}")
        if self._is_at_cave_entrance(state):
            return self._explore_cave_entrance(state)

        return {"narration": "explore"}

    @staticmethod
    def _is_at_cave_entrance(state: GameState) -> bool:
        return state["current_room"]["id"] == "cave_entrance"

    def _explore_cave_entrance(self, state: GameState) -> GameState:
        if state["action"]["explore_option"] == "forward":
            room = state["current_room"]["next_room"]
            return self._describe_room(room)
        elif state["action"]["explore_option"] == "look":
            room = state["current_room"]
            return self._describe_room(room)
        else:
            return {"narration": "You cannot run away.  You must enter the cave."}

    def _describe_room(self, room: DungeonRoom) -> GameState:
        msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "Describe the room to the player using only the facts from the room."
                    f"\nThe room is: {room}",
                }
            ]
        }
        result = self._dungeon_master_agent.invoke(msg)
        response = result["structured_response"]
        return {"narration": response.narration, "current_room": room}

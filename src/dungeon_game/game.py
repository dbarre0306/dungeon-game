import os
import pprint
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from dungeon_game.dungeon import DungeonFactory, DungeonRoom

load_dotenv()

ActionType = Literal["explore", "combat", "unknown"]
ExploreOption = Literal["left", "right", "forward", "backward", "look"]


class PlayerState(TypedDict):
    player_type: Literal["warrior", "mage"]
    health_points: int


class Action(TypedDict):
    action: ActionType | None
    explore_option: ExploreOption | None


class GameState(TypedDict):
    player: PlayerState
    command: str
    action: Action
    narration: str
    current_room: DungeonRoom


class Instructions(BaseModel):
    text: str


class RouterState(BaseModel):
    # action: Literal["combat", "shop", "explore", "multiple", "unknown"] = Field(
    action: ActionType = Field(description="Action")
    explore_option: ExploreOption | None = Field(
        description="Which direction the player wants to move or if they are just looking around."
    )


class GameUpdate(BaseModel):
    player_health_points: int | None
    enemy_health_points: int | None
    narration: str


class Game:

    def __init__(self):
        model = f"openai:{os.getenv("MODEL", "gpt-4o-mini")}"
        self.router_agent = create_agent(
            model=model,
            system_prompt="You are great at categorizing commands from the player.",
            response_format=RouterState,
        )

        self.dungeon_master_agent = create_agent(
            model=model,
            system_prompt="You are the Dungeon Master for this game. "
            "The game is similar to Dungeons and Dragons.  As the Dungeon Master "
            "you control the flow of the game through narration.  You have a way "
            "with words in that you can make it fun and scary at the same time. "
            "In this game, the player must retrieve the Amulet of Valdorin that was "
            "was stolen by a troll who lives in the Dungeon of Mistwood.",
            response_format=GameUpdate,
        )

    def run(self) -> None:

        print("Generating Dungeon")
        dungeon_factory = DungeonFactory()
        dungeon_room = dungeon_factory.generate()
        print("Generating Dungeon completed")

        agent_builder = StateGraph(GameState)

        # Add nodes
        agent_builder.add_node("router", self.router)
        agent_builder.add_node("explore", self.explore)
        agent_builder.add_node("combat", self.combat)
        agent_builder.add_node("unknown", self.unknown)

        # Add edges to connect nodes
        agent_builder.add_edge(START, "router")
        agent_builder.add_conditional_edges(
            "router", self.next_action, ["explore", "combat", "unknown"]
        )
        agent_builder.add_edge("explore", END)
        agent_builder.add_edge("combat", END)
        agent_builder.add_edge("unknown", END)

        # Compile the agent
        agent = agent_builder.compile()

        state = self.initial_game_state(dungeon_room)

        command = input("> ")
        while command != "x":
            state["command"] = command
            state = agent.invoke(state)
            pprint.pprint(state["narration"])
            pprint.pprint(f"Room: {state["current_room"]["id"]}")
            command = input("> ")

    def initial_game_state(self, dungeon_room: DungeonRoom) -> GameState:
        return {
            "player": {
                "player_type": "warrior",
                "health_points": 10,
            },
            "current_room": dungeon_room,
        }

    def router(self, state: GameState) -> GameState:
        content = (
            f"Player command: {state["command"]}\n"
            "\n"
            "Do your best to categorize the player's command "
            "to either explore or combat.  If there is no match, categorize it as unknown. "
            "\n"
            "Exploring encompasses both moving, entering, or looking around. If just looking around, "
            "set the explore_option to `look`.  If moving or entering, set the explore_option to be the "
            "player's direction which is either "
            "`left`, `right`, `forward`, or `backward`.  If the player's command doesn't specify "
            "the direction, the use `forward` by default."
        )
        result = self.router_agent.invoke(
            {"messages": [{"role": "user", "content": content}]}
        )
        return {
            "action": {
                "action": result["structured_response"].action,
                "explore_option": result["structured_response"].explore_option,
            }
        }

    def explore(self, state: GameState) -> GameState:
        pprint.pprint(f"Explore Room: {state["current_room"]["id"]}")
        if self.is_at_cave_entrance(state):
            return self.explore_cave_entrance(state)

        return {"narration": "explore"}

    def combat(self, state: GameState) -> GameState:
        # self.combat_agent.invoke({"messages": [{"role": "user", "content": ""}]})
        return {"narration": "combat"}

    def unknown(self, state: GameState) -> GameState:
        return {"narration": "I don't understand what you are saying."}

    def next_action(self, state: GameState) -> ActionType:
        return state["action"]["action"]

    @staticmethod
    def is_at_cave_entrance(state: GameState) -> bool:
        return state["current_room"]["id"] == "cave_entrance"

    def explore_cave_entrance(self, state: GameState) -> GameState:
        if state["action"]["explore_option"] != "forward":
            return {"narration": "You cannot run away.  You must enter the cave."}
        else:
            return self.describe_next_room(state)

    def describe_next_room(self, state: GameState) -> GameState:
        next_room = state["current_room"]["next_room"]
        msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "Describe the room to the player using only the facts from the next room. "
                    f"\nThe next room is: {next_room}",
                }
            ]
        }
        result = self.dungeon_master_agent.invoke(msg)
        response = result["structured_response"]
        return {"narration": response.narration, "current_room": next_room}

    # TODO: probably won't need this
    # def human_message(self, room: DungeonRoom) -> dict:
    #     content = (
    #         "Facts:\n"
    #         f"{self.format_facts(room["facts"])}"
    #     )

    #     return {"messages": [{"role": "user", "content": content}]}

    # @staticmethod
    # def format_facts(facts: list[str]) -> str:
    #     return "\n".join(map(lambda f: f"- {f}", facts))

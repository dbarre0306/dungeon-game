import os
import pprint
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from dungeon_game.actions.explore import ExploreNode
from dungeon_game.dungeon import DungeonFactory, DungeonRoom
from dungeon_game.game_state import ActionType, ExploreOption, GameState

load_dotenv()


class Instructions(BaseModel):
    text: str


class RouterState(BaseModel):
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

        self.explore_node = ExploreNode(self.dungeon_master_agent)

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
        agent_builder.add_node("shop", self.shop)
        agent_builder.add_node("drink_potion", self.drink_potion)
        agent_builder.add_node("open_chest", self.open_chest)
        agent_builder.add_node("multiple", self.multiple)
        agent_builder.add_node("unknown", self.unknown)

        # Add edges to connect nodes
        agent_builder.add_edge(START, "router")
        agent_builder.add_conditional_edges(
            "router",
            self.next_action,
            [
                "explore",
                "combat",
                "shop",
                "drink_potion",
                "open_chest",
                "multiple",
                "unknown",
            ],
        )
        agent_builder.add_edge("explore", END)
        agent_builder.add_edge("combat", END)
        agent_builder.add_edge("unknown", END)

        # Compile the agent
        agent = agent_builder.compile()

        state = self.initial_game_state(dungeon_room)

        state["command"] = "look around"
        state = agent.invoke(state)
        pprint.pprint(state["narration"])
        pprint.pprint(f"Room: {state["current_room"]["id"]}")

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
            "Do your best to categorize the player's command to only one of the "
            "following categories: explore, combat, shop, drink_potion, or open_chest. "
            "If the command matches multiple categories, then categorize it as multiple. "
            "If there is no match, categorize it as unknown. "
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
        return self.explore_node.execute(state)

    def combat(self, state: GameState) -> GameState:
        # self.combat_agent.invoke({"messages": [{"role": "user", "content": ""}]})
        return {"narration": "combat"}

    def shop(self, state: GameState) -> GameState:
        return {"narration": "shop"}

    def drink_potion(self, state: GameState) -> GameState:
        return {"narration": "drink_potion"}

    def open_chest(self, state: GameState) -> GameState:
        return {"narration": "open_chest"}

    def multiple(self, state: GameState) -> GameState:
        return {"narration": "You can only do one action at a time."}

    def unknown(self, state: GameState) -> GameState:
        return {"narration": "I don't understand what you are saying."}

    def next_action(self, state: GameState) -> ActionType:
        return state["action"]["action"]

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

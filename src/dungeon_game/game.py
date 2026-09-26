import os
import pprint
from collections.abc import Callable
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.agents.structured_output import StructuredOutputError
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from dungeon_game.actions.explore import ExploreNode
from dungeon_game.dungeon import DungeonFactory, DungeonRoom
from dungeon_game.game_state import ActionType, ExploreOption, GameState, Player

load_dotenv()


class Instructions(BaseModel):
    text: str


class RouterState(BaseModel):
    action: ActionType = Field(description="Action")
    explore_option: ExploreOption | None = Field(
        default=None,
        description="Which direction the player wants to move or if they are just looking around.",
    )


# TODO: rename to DungeonMasterResponse
class GameUpdate(BaseModel):
    player_health_points: int | None
    enemy_health_points: int | None
    narration: str


@wrap_model_call
def retry_on_invalid_structured_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Guardrail: retry a model call that returns malformed structured output.

    Small models occasionally hallucinate invalid tool-call arguments for
    optional Literal fields (e.g. echoing back the field's JSON schema
    instead of a real value), which raises StructuredOutputError. Retrying
    gives the model another chance to produce a valid response before we
    give up on the whole turn.
    """
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            return handler(request)
        except StructuredOutputError:
            if attempt == max_attempts - 1:
                raise


class Game:

    def __init__(self):
        model = f"openai:{os.getenv("MODEL", "gpt-4o-mini")}"
        self.router_agent = create_agent(
            model=model,
            system_prompt="You are great at categorizing commands from the player.",
            response_format=RouterState,
            middleware=[retry_on_invalid_structured_output],
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
                # "get_coins",
                "multiple",
                "unknown",
            ],
        )
        agent_builder.add_edge("explore", END)
        agent_builder.add_edge("combat", END)
        # agent_builder.add_edge("counter_attack", END)
        agent_builder.add_edge("shop", END)
        agent_builder.add_edge("drink_potion", END)
        agent_builder.add_edge("open_chest", END)
        agent_builder.add_edge("multiple", END)
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
            "player": self.create_player(),
            "current_room": dungeon_room,
        }

    def create_player(self) -> Player:
        return {
            "player_type": "warrior",
            "max_health_points": 25,
            "health_points": 10,
            "is_fighting": False,
            "offensive_weapon": {
                "name": "Bronze Sword",
                "bonus_points": 3,
            },
            "defensive_weapon": {
                "name": "Bronze Shield",
                "health_points": 2,
                "condition": "good",
            },
            "healiing_powers": [{"name": "Potion", "health_points": 8, "quantity": 2}],
        }

    def router(self, state: GameState) -> GameState:
        content = (
            f"Player command: {state["command"]}\n"
            "\n"
            "Do your best to categorize the player's command to only one of the "
            "following categories: `explore`, `combat`, `shop`, `drink_potion`, or `open_chest`. "
            "If the command matches multiple categories, then categorize it as `multiple`. "
            "If there is no match, categorize it as `unknown`. "
            "\n"
            "Exploring encompasses both moving, entering, or looking around. If just looking around, "
            "set the explore_option to `look`.  If moving or entering, set the explore_option to be the "
            "player's direction which is either "
            "`left`, `right`, `forward`, or `backward`.  If the player's command doesn't specify "
            "the direction, then use `forward` by default."
        )
        try:
            result = self.router_agent.invoke(
                {"messages": [{"role": "user", "content": content}]}
            )
        except StructuredOutputError:
            # The model occasionally returns malformed structured output
            # (e.g. for typos or ambiguous commands). Treat it as unknown
            # rather than crashing the whole game loop.
            return {"action": {"action": "unknown", "explore_option": None}}
        return {
            "action": {
                "action": result["structured_response"].action,
                "explore_option": result["structured_response"].explore_option,
            }
        }

    def explore(self, state: GameState) -> GameState:
        return self.explore_node.execute(state)

    def combat(self, state: GameState) -> GameState:
        return {"narration": "combat"}

    def shop(self, state: GameState) -> GameState:
        return {"narration": "shop"}

    def drink_potion(self, state: GameState) -> GameState:
        return {"narration": "drink_potion"}

    def open_chest(self, state: GameState) -> GameState:
        return {"narration": "open_chest"}

    def multiple(self, state: GameState) -> GameState:
        return {"narration": "You can only perform one action at a time."}

    def unknown(self, state: GameState) -> GameState:
        return {"narration": "I don't understand what you are saying."}

    def next_action(self, state: GameState) -> ActionType:
        return state["action"]["action"]

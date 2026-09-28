import os
import pprint

from dotenv import load_dotenv
from langchain.agents.structured_output import StructuredOutputError
from langgraph.graph import END, START, StateGraph

from dungeon_game.actions.explore import ExploreNode
from dungeon_game.agents.dungeon_master_agent import create_dungeon_master_agent
from dungeon_game.agents.router_agent import create_router_agent
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from dungeon_game.domain.misc.action import ActionType
from dungeon_game.domain.player.warrior import create_default_warrior
from dungeon_game.game_state import GameState

load_dotenv()


class Game:

    def __init__(self):
        model = f"openai:{os.getenv("MODEL", "gpt-4o-mini")}"
        self.router_agent = create_router_agent(model)
        self.dungeon_master_agent = create_dungeon_master_agent(model)
        self.explore_node = ExploreNode(self.dungeon_master_agent)

    def run(self) -> None:

        print("Generating Dungeon")
        dungeon_factory = DungeonFactory()
        dungeon = dungeon_factory.generate()
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

        state = self.initial_game_state(dungeon, "look around")
        state = GameState.model_validate(agent.invoke(state))
        pprint.pprint(state.narration)
        pprint.pprint(f"Room: {self.current_room(state).type}")

        command = input("> ")
        while command != "x":
            state = state.model_copy(update={"command": command})
            state = GameState.model_validate(agent.invoke(state))
            pprint.pprint(state.narration)
            pprint.pprint(f"Room: {self.current_room(state).type}")
            command = input("> ")

    def current_room(self, state: GameState):
        return state.dungeon.get_room(state.player.current_room_index)

    def initial_game_state(self, dungeon: Dungeon, command: str) -> GameState:
        return GameState(
            player=create_default_warrior(),
            dungeon=dungeon,
            command=command,
        )

    def router(self, state: GameState) -> GameState:
        content = (
            f"Player command: {state.command}\n"
            "\n"
            "Do your best to categorize the player's command to only one of the "
            "following categories: `explore`, `combat`, `shop`, `drink_potion`, or `open_chest`. "
            "If the command matches multiple categories, then categorize it as `multiple`. "
            "If there is no match, categorize it as `unknown`. "
            "\n"
            "Exploring encompasses both moving, entering, or looking around. If just looking "
            "around, set the explore_option to `look`.  If moving or entering, set the "
            "explore_option to be the player's direction which is either "
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
        return state.action.action

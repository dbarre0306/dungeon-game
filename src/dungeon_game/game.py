import os
import pprint
from typing import Any

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from dungeon_game.agents.dungeon_master_agent import create_dungeon_master_agent
from dungeon_game.agents.router_agent import create_router_agent
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from dungeon_game.domain.misc.action import ActionType
from dungeon_game.domain.player.warrior import create_default_warrior
from dungeon_game.game_state import GameState
from dungeon_game.nodes.combat import CombatNode
from dungeon_game.nodes.drink_potion import DrinkPotionNode
from dungeon_game.nodes.explore import ExploreNode
from dungeon_game.nodes.open_chest import OpenChestNode
from dungeon_game.nodes.router import RouterNode
from dungeon_game.nodes.shop import ShopNode

load_dotenv()


class Game:

    def __init__(self):
        model = f"openai:{os.getenv("MODEL", "gpt-4o-mini")}"
        self.router_agent = create_router_agent(model)
        self.dungeon_master_agent = create_dungeon_master_agent(model)
        self.router_node = RouterNode(self.router_agent)
        self.explore_node = ExploreNode(self.dungeon_master_agent)
        self.combat_node = CombatNode()
        self.shop_node = ShopNode()
        self.drink_potion_node = DrinkPotionNode()
        self.open_chest_node = OpenChestNode()

    def run(self) -> None:

        print("Generating Dungeon")
        dungeon_factory = DungeonFactory()
        dungeon = dungeon_factory.generate()
        print("Generating Dungeon completed")

        agent_builder = StateGraph(GameState)

        # Add nodes
        agent_builder.add_node("router", self.router_node.execute)
        agent_builder.add_node("explore", self.explore_node.execute)
        agent_builder.add_node("combat", self.combat_node.execute)
        agent_builder.add_node("shop", self.shop_node.execute)
        agent_builder.add_node("drink_potion", self.drink_potion_node.execute)
        agent_builder.add_node("open_chest", self.open_chest_node.execute)
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

    def multiple(self, state: GameState) -> dict[str, Any]:
        return {"narration": "You can only perform one action at a time."}

    def unknown(self, state: GameState) -> dict[str, Any]:
        return {"narration": "I don't understand what you are saying."}

    def next_action(self, state: GameState) -> ActionType:
        return state.action.action

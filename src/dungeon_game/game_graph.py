import os
from typing import Any

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from dungeon_game.agents.dungeon_master_agent import create_dungeon_master_agent
from dungeon_game.agents.router_agent import create_router_agent
from dungeon_game.domain.intent import ActionType
from dungeon_game.game_state import GameState
from dungeon_game.nodes.attack import AttackNode
from dungeon_game.nodes.drink_potion import DrinkPotionNode
from dungeon_game.nodes.enemy_attack import EnemyAttackNode
from dungeon_game.nodes.explore import ExploreNode
from dungeon_game.nodes.open_chest import OpenChestNode
from dungeon_game.nodes.router import RouterNode
from dungeon_game.nodes.shop import ShopNode

load_dotenv()


class GameGraph:

    def __init__(self):
        model = f"openai:{os.getenv("MODEL", "gpt-4o-mini")}"
        router_agent = create_router_agent(model)
        dungeon_master_agent = create_dungeon_master_agent(model)
        self.router_node = RouterNode(router_agent)
        self.explore_node = ExploreNode(dungeon_master_agent)
        self.attack_node = AttackNode()
        self.enemy_attack_node = EnemyAttackNode()
        self.shop_node = ShopNode()
        self.drink_potion_node = DrinkPotionNode()
        self.open_chest_node = OpenChestNode()

        self.agent = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(GameState)

        # Add nodes
        graph_builder.add_node("router", self.router_node.execute)
        graph_builder.add_node("explore", self.explore_node.execute)
        graph_builder.add_node("attack", self.attack_node.execute)
        graph_builder.add_node("enemy_attack", self.enemy_attack_node.execute)
        graph_builder.add_node("shop", self.shop_node.execute)
        graph_builder.add_node("drink_potion", self.drink_potion_node.execute)
        graph_builder.add_node("open_chest", self.open_chest_node.execute)
        graph_builder.add_node("multiple", self._multiple)
        graph_builder.add_node("unknown", self._unknown)

        # Add edges to connect nodes
        graph_builder.add_edge(START, "router")
        graph_builder.add_conditional_edges(
            "router",
            self._next_action,
            [
                "explore",
                "attack",
                "shop",
                "drink_potion",
                "open_chest",
                # "get_coins",
                "multiple",
                "unknown",
            ],
        )
        graph_builder.add_edge("explore", END)
        graph_builder.add_edge("attack", "enemy_attack")
        graph_builder.add_edge("enemy_attack", END)  # If enemy is dead, do not go here
        graph_builder.add_edge("shop", END)
        graph_builder.add_edge("drink_potion", END)
        graph_builder.add_edge("open_chest", END)
        graph_builder.add_edge("multiple", END)
        graph_builder.add_edge("unknown", END)

        return graph_builder.compile()

    def invoke(self, state: GameState) -> GameState:
        return GameState.model_validate(self.agent.invoke(state))

    def _multiple(self, state: GameState) -> dict[str, Any]:
        return {"narration": "You can only perform one action at a time."}

    def _unknown(self, state: GameState) -> dict[str, Any]:
        return {"narration": "I don't understand what you are saying."}

    def _next_action(self, state: GameState) -> ActionType:
        return state.action.type

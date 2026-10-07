from typing import Any

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.game_state import GameState
from dungeon_game.nodes.drink_potion import DrinkPotionNode
from dungeon_game.nodes.enemy_attack import EnemyAttackNode
from dungeon_game.nodes.explore import ExploreNode
from dungeon_game.nodes.look import LookNode
from dungeon_game.nodes.open_chest import OpenChestNode
from dungeon_game.nodes.player_attack import PlayerAttackNode
from dungeon_game.nodes.router import RouterNode
from dungeon_game.nodes.shop import ShopNode

load_dotenv()


class GameGraph:
    def __init__(
        self, router_agent: RouterAgent, dungeon_master_agent: DungeonMasterAgent
    ):
        self._dungeon_master_agent = dungeon_master_agent
        self.router_node = RouterNode(router_agent)
        self.explore_node = ExploreNode(dungeon_master_agent)
        self.look_node = LookNode(dungeon_master_agent)
        self.player_attack_node = PlayerAttackNode(dungeon_master_agent)
        self.enemy_attack_node = EnemyAttackNode(dungeon_master_agent)
        self.shop_node = ShopNode()
        self.drink_potion_node = DrinkPotionNode(dungeon_master_agent)
        self.open_chest_node = OpenChestNode()

        self.agent = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(GameState)

        # Add nodes
        graph_builder.add_node("router", self.router_node.execute)
        graph_builder.add_node("explore", self.explore_node.execute)
        graph_builder.add_node("look", self.look_node.execute)
        graph_builder.add_node("player_attack", self.player_attack_node.execute)
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
                "look",
                "player_attack",
                "shop",
                "drink_potion",
                "open_chest",
                # "get_coins",
                "multiple",
                "unknown",
            ],
        )
        graph_builder.add_edge("explore", END)
        graph_builder.add_edge("look", END)
        graph_builder.add_conditional_edges(
            "player_attack", self._player_is_fighting, ["enemy_attack", END]
        )
        graph_builder.add_edge("enemy_attack", END)  # If enemy is dead, do not go here
        graph_builder.add_edge("shop", END)
        graph_builder.add_edge("drink_potion", END)
        graph_builder.add_conditional_edges(
            "drink_potion", self._player_is_fighting, ["enemy_attack", END]
        )
        graph_builder.add_edge("open_chest", END)
        graph_builder.add_edge("multiple", END)
        graph_builder.add_edge("unknown", END)

        return graph_builder.compile()

    def invoke(self, state: GameState) -> GameState:
        state = state.model_copy(update={"narration": []})
        return GameState.model_validate(self.agent.invoke(state))

    def _multiple(self, state: GameState) -> dict[str, Any]:
        return {"narration": ["You can only perform one action at a time."]}

    def _unknown(self, state: GameState) -> dict[str, Any]:
        msg = (
            "Tell the player that what they want to do "
            "doesn't make any sense given the room they are in."
        )
        response = self._dungeon_master_agent.invoke(
            state.get_current_room(), state.player, msg
        )
        return {"narration": [response.narration]}

    def _next_action(self, state: GameState) -> str:
        if state.intent.type == "attack":
            return "player_attack"
        return state.intent.type

    def _player_is_fighting(self, state: GameState) -> str:
        return "enemy_attack" if state.player.is_fighting else END

from typing import Any

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.domain.dice import Dice
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.domain.rooms.trap_room import TrapRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.cast_healing import CastHealingNode
from dungeon_game.nodes.cross_trap import CrossTrapNode
from dungeon_game.nodes.drink_potion import DrinkPotionNode
from dungeon_game.nodes.enemy_attack import EnemyAttackNode
from dungeon_game.nodes.explore import ExploreNode
from dungeon_game.nodes.game_over import GameOverNode
from dungeon_game.nodes.intro import IntroNode
from dungeon_game.nodes.look import LookNode
from dungeon_game.nodes.open_chest import OpenChestNode
from dungeon_game.nodes.player_attack import PlayerAttackNode
from dungeon_game.nodes.router import RouterNode
from dungeon_game.nodes.shop import ShopNode

load_dotenv()


class GameGraph:
    def __init__(
        self,
        router_agent: RouterAgent,
        dungeon_master_agent: DungeonMasterAgent,
        dice: Dice | None = None,
    ):
        dice = dice or Dice()
        self._dungeon_master_agent = dungeon_master_agent
        self.intro_node = IntroNode(dungeon_master_agent)
        self.router_node = RouterNode(router_agent)
        self.explore_node = ExploreNode(dungeon_master_agent)
        self.cross_trap_node = CrossTrapNode(dungeon_master_agent, dice)
        self.look_node = LookNode(dungeon_master_agent)
        self.player_attack_node = PlayerAttackNode(dungeon_master_agent, dice)
        self.enemy_attack_node = EnemyAttackNode(dungeon_master_agent, dice)
        self.shop_node = ShopNode(dungeon_master_agent)
        self.drink_potion_node = DrinkPotionNode(dungeon_master_agent)
        self.cast_healing_node = CastHealingNode(dungeon_master_agent)
        self.open_chest_node = OpenChestNode(dungeon_master_agent, dice)
        self.game_over_node = GameOverNode(dungeon_master_agent)

        self.agent = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(GameState)

        # Add nodes
        graph_builder.add_node("intro", self.intro_node.execute)
        graph_builder.add_node("router", self.router_node.execute)
        graph_builder.add_node("explore", self.explore_node.execute)
        graph_builder.add_node("cross_trap", self.cross_trap_node.execute)
        graph_builder.add_node("look", self.look_node.execute)
        graph_builder.add_node("player_attack", self.player_attack_node.execute)
        graph_builder.add_node("enemy_attack", self.enemy_attack_node.execute)
        graph_builder.add_node("shop", self.shop_node.execute)
        graph_builder.add_node("drink_potion", self.drink_potion_node.execute)
        graph_builder.add_node("cast_healing", self.cast_healing_node.execute)
        graph_builder.add_node("open_chest", self.open_chest_node.execute)
        graph_builder.add_node("game_over", self.game_over_node.execute)
        graph_builder.add_node("multiple", self._multiple)
        graph_builder.add_node("illegal", self._illegal)
        graph_builder.add_node("unknown", self._unknown)

        # Add edges to connect nodes
        graph_builder.add_conditional_edges(START, self._entry, ["intro", "router"])
        graph_builder.add_edge("intro", END)
        graph_builder.add_conditional_edges(
            "router",
            self._next_action,
            [
                "explore",
                "cross_trap",
                "look",
                "player_attack",
                "shop",
                "drink_potion",
                "cast_healing",
                "open_chest",
                "multiple",
                "unknown",
                "illegal",
            ],
        )
        graph_builder.add_conditional_edges(
            "explore", self._enemy_strikes_after_failed_attempt, ["enemy_attack", END]
        )
        graph_builder.add_edge("cross_trap", "game_over")
        graph_builder.add_edge("look", END)
        graph_builder.add_conditional_edges(
            "player_attack",
            self._after_player_attack,
            ["enemy_attack", "game_over", END],
        )
        graph_builder.add_edge("enemy_attack", "game_over")
        graph_builder.add_edge("game_over", END)
        graph_builder.add_edge("shop", END)
        graph_builder.add_conditional_edges(
            "drink_potion", self._player_is_fighting, ["enemy_attack", END]
        )
        graph_builder.add_conditional_edges(
            "cast_healing", self._player_is_fighting, ["enemy_attack", END]
        )
        graph_builder.add_conditional_edges(
            "open_chest",
            self._enemy_strikes_after_failed_attempt,
            ["enemy_attack", END],
        )
        graph_builder.add_edge("multiple", END)
        graph_builder.add_edge("unknown", END)
        graph_builder.add_edge("illegal", END)

        return graph_builder.compile()

    def invoke(self, state: GameState) -> GameState:
        state = state.model_copy(update={"narration": [], "attempt_failed": False})
        return GameState.model_validate(self.agent.invoke(state))

    def _multiple(self, state: GameState) -> dict[str, Any]:
        print("MULTIPLE Command")
        return {"narration": ["You can only perform one action at a time."]}

    def _unknown(self, state: GameState) -> dict[str, Any]:
        print("UNKNOWN Command")
        msg = (
            "Tell the player that what they want to do "
            "doesn't make any sense given the room they are in."
        )
        response = self._dungeon_master_agent.invoke(state, msg, include_command=True)
        return {"narration": [response.narration]}

    def _illegal(self, state: GameState) -> dict[str, Any]:
        """The room does not allow this intent: tell the player and do nothing
        else, even in a fight."""
        _, msg = state.get_current_room().is_valid_intent(state.intent)
        msg = msg or "Tell the player that they can't do that here."
        response = self._dungeon_master_agent.invoke(state, msg, include_command=True)
        return {"narration": [response.narration]}

    @staticmethod
    def _entry(state: GameState) -> str:
        return "intro" if state.opening else "router"

    def _next_action(self, state: GameState) -> str:
        intent = state.intent
        if intent.type in ("multiple", "unknown"):
            return intent.type
        room = state.get_current_room()
        if intent.type not in room.get_legal_intents(state.player):
            return "illegal"
        if intent.type == "attack":
            return "player_attack"
        if intent.is_explore_forward() and self._is_trap_unsprung(state):
            return "cross_trap"
        return intent.type

    @staticmethod
    def _enemy_strikes_after_failed_attempt(state: GameState) -> str:
        """A legal attempt the room refuses while the player is fighting costs
        the player their turn: the enemy strikes after it is narrated."""
        return (
            "enemy_attack" if state.attempt_failed and state.player.is_fighting else END
        )

    @staticmethod
    def _is_trap_unsprung(state: GameState) -> bool:
        room = state.get_current_room()
        return isinstance(room, TrapRoom) and not room.is_sprung

    def _after_player_attack(self, state: GameState) -> str:
        """The enemy strikes back if the fight goes on; killing the troll wins
        the game."""
        room = state.get_current_room()
        if isinstance(room, ThroneRoom) and room.enemy.is_dead():
            return "game_over"
        return self._player_is_fighting(state)

    def _player_is_fighting(self, state: GameState) -> str:
        return "enemy_attack" if state.player.is_fighting else END

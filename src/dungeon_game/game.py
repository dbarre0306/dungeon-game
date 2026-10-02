import os
import pprint

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from dungeon_game.domain.player.player import Player
from dungeon_game.domain.player.warrior import create_default_warrior
from dungeon_game.game_graph import GameGraph
from dungeon_game.game_state import GameState


class Game:
    def __init__(self):
        print("Generating Dungeon")
        dungeon_factory = DungeonFactory()
        self.dungeon = dungeon_factory.generate()
        print("Generating Dungeon completed")

        self.player = create_default_warrior()

        model = f"openai:{os.getenv('MODEL', 'gpt-4o-mini')}"
        router_agent = RouterAgent(model)
        dungeon_master_agent = DungeonMasterAgent(model, self.game_facts(self.player))

        self.game_graph = GameGraph(router_agent, dungeon_master_agent)

    def game_facts(self, player: Player) -> list[str]:
        return [player.get_facts()]

    def run(self) -> None:

        state = GameState(player=self.player, dungeon=self.dungeon, command="look")
        state = self.game_graph.invoke(state)
        self._print_narration(state.narration)
        pprint.pprint(f"Room: {state.get_current_room().type}")
        pprint.pprint(f"Player HP: {state.player.health_points}")

        command = input("> ")
        while command != "x":
            state = state.model_copy(update={"command": command})
            state = self.game_graph.invoke(state)
            self._print_narration(state.narration)
            pprint.pprint(f"Room: {state.get_current_room().type}")
            pprint.pprint(f"Player HP: {state.player.health_points}")
            pprint.pprint(f"Player potions: {state.player.potions.quantity}")
            command = input("> ")

    def _print_narration(self, narration: list[str]):
        print("\n".join(narration))

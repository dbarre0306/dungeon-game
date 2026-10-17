import os

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from dungeon_game.game_graph import GameGraph
from dungeon_game.game_state import GameState


class Game:
    def __init__(self):
        self.player = create_default_warrior()
        merchant = Merchant(merchandise=self.player.get_supported_merchandise())

        print("Generating Dungeon")
        dungeon_factory = DungeonFactory()
        self.dungeon = dungeon_factory.generate(merchant)
        print("Generating Dungeon completed")

        model_name = os.getenv("MODEL", "gpt-4o-mini")
        # A bare name defaults to OpenAI; "provider:name" is used as given.
        model = model_name if ":" in model_name else f"openai:{model_name}"
        router_agent = RouterAgent(model)
        dungeon_master_agent = DungeonMasterAgent(model)

        self.game_graph = GameGraph(router_agent, dungeon_master_agent)

    def run(self) -> None:

        state = GameState(player=self.player, dungeon=self.dungeon, command="look")
        state = self.game_graph.invoke(state)
        self._print_narration(state.narration)
        print(f"Room: {state.get_current_room().type}")
        state.player.print()

        while not state.game_over:
            command = input("> ")
            if command == "x":
                break
            state = state.model_copy(update={"command": command})
            state = self.game_graph.invoke(state)
            self._print_narration(state.narration)
            print(f"Room: {state.get_current_room().type}")
            state.player.print()

        if state.game_over:
            print("GAME OVER")

    def _print_narration(self, narration: list[str]):
        print("\n".join(narration))

import pprint

from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from dungeon_game.domain.player.warrior import create_default_warrior
from dungeon_game.game_graph import GameGraph
from dungeon_game.game_state import GameState


class Game:

    def __init__(self):
        self.game_graph = GameGraph()

    def run(self) -> None:

        print("Generating Dungeon")
        dungeon_factory = DungeonFactory()
        dungeon = dungeon_factory.generate()
        print("Generating Dungeon completed")

        state = self.initial_game_state(dungeon, "look around")
        state = self.game_graph.invoke(state)
        print(state.narration)
        pprint.pprint(f"Room: {self.current_room(state).type}")

        command = input("> ")
        while command != "x":
            state = state.model_copy(update={"command": command})
            state = self.game_graph.invoke(state)
            print(state.narration)
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

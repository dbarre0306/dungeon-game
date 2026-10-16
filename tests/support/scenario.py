from dungeon_game.agents.router_agent import RouterState
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.game_graph import GameGraph
from dungeon_game.game_state import GameState
from tests.support.builders import full_dungeon, goblin, monster_dungeon
from tests.support.fakes import FakeDice, FakeDungeonMaster, FakeRouterAgent


class Scenario:
    """A game driven one player command at a time, with the router, Dungeon
    Master and dice faked. The player starts in the room at `room_index`."""

    def __init__(
        self,
        routes: dict[str, RouterState],
        dungeon: Dungeon | None = None,
        room_index: int = 0,
        dice: FakeDice | None = None,
    ):
        self.dm = FakeDungeonMaster()
        self.dice = dice or FakeDice()
        self.graph = GameGraph(FakeRouterAgent(routes), self.dm, self.dice)
        player = create_default_warrior().model_copy(
            update={"current_room_index": room_index}
        )
        self.state = GameState(
            player=player,
            dungeon=dungeon or full_dungeon(),
            command="",
        )

    def say(self, command: str) -> GameState:
        self.state = self.graph.invoke(
            self.state.model_copy(update={"command": command})
        )
        return self.state

    @property
    def room_type(self) -> str:
        return self.state.get_current_room().type


MONSTER_ROOM = 0

FIGHT_ROUTES = {
    "attack": RouterState(intent="attack"),
    "drink": RouterState(intent="drink_potion"),
    "go forward": RouterState(intent="explore", explore_direction="forward"),
}


def fight(
    *rolls: int,
    health_points: int = 20,
    potions: int = 2,
    goblin_health_points: int = 10,
) -> Scenario:
    """A fight in the monster room with the dice scripted and the warrior's
    health and potions, and the goblin's health, as given. The commands are
    "attack", "drink" and "go forward"."""
    game = Scenario(
        FIGHT_ROUTES,
        dungeon=monster_dungeon(goblin(health_points=goblin_health_points)),
        room_index=MONSTER_ROOM,
        dice=FakeDice(*rolls),
    )
    player = game.state.player
    game.state = game.state.model_copy(
        update={
            "player": player.model_copy(
                update={
                    "health_points": health_points,
                    "potions": player.potions.model_copy(update={"quantity": potions}),
                }
            )
        }
    )
    return game

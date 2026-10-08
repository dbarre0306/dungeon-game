"""Use cases at the cave entrance: the player can only enter the cave by going
forward; any other direction is refused and they stay where they are."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.game_graph import GameGraph
from dungeon_game.game_state import GameState
from tests.support.builders import monster_dungeon
from tests.support.fakes import FakeDice, FakeDungeonMaster, FakeRouterAgent

ROUTES = {
    "go forward": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "go right": RouterState(intent="explore", explore_direction="right"),
    "go back": RouterState(intent="explore", explore_direction="backward"),
    "look around": RouterState(intent="look"),
}


class Scenario:
    """A game at the cave entrance, driven one player command at a time."""

    def __init__(self):
        self.dm = FakeDungeonMaster()
        self.graph = GameGraph(FakeRouterAgent(ROUTES), self.dm, FakeDice())
        self.state = GameState(
            player=create_default_warrior(),
            dungeon=monster_dungeon(),
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


@pytest.fixture
def game() -> Scenario:
    return Scenario()


def test_player_starts_at_the_cave_entrance(game):
    assert game.room_type == "cave_entrance"


def test_going_forward_enters_the_cave(game):
    state = game.say("go forward")

    assert game.room_type == "cave_chamber"
    assert len(state.narration) == 1
    assert state.get_current_room().history == state.narration


@pytest.mark.parametrize("command", ["go left", "go right", "go back"])
def test_going_any_other_direction_is_refused(game, command):
    state = game.say(command)

    assert game.room_type == "cave_entrance"
    assert len(state.narration) == 1
    assert "cannot go that way" in game.dm.messages[0]
    assert "must enter the cave" in game.dm.messages[0]


def test_player_can_enter_the_cave_after_being_refused(game):
    game.say("go left")
    game.say("go forward")

    assert game.room_type == "cave_chamber"


def test_looking_describes_the_entrance_and_keeps_the_player_there(game):
    state = game.say("look around")

    assert game.room_type == "cave_entrance"
    assert len(state.narration) == 1
    assert state.get_current_room().history == state.narration


def test_looking_again_narrates_without_repeating_the_room_history(game):
    first = game.say("look around").narration
    second = game.say("look around").narration

    assert len(second) == 1
    assert game.room_type == "cave_entrance"
    assert game.state.get_current_room().history == first


def test_player_can_enter_the_cave_after_looking(game):
    game.say("look around")
    game.say("go forward")

    assert game.room_type == "cave_chamber"

"""Use cases in the cave chamber: the player can only leave by going left or
right; forward and backward are refused and they stay where they are."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.scenario import Scenario

CAVE_CHAMBER = 1

ROUTES = {
    "go forward": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "go right": RouterState(intent="explore", explore_direction="right"),
    "go back": RouterState(intent="explore", explore_direction="backward"),
    "look around": RouterState(intent="look"),
}


@pytest.fixture
def game() -> Scenario:
    return Scenario(ROUTES, room_index=CAVE_CHAMBER)


@pytest.mark.parametrize("command", ["go left", "go right"])
def test_going_left_or_right_leaves_the_chamber(game, command):
    state = game.say(command)

    assert game.room_type == "monster_room"
    assert len(state.narration) == 1
    assert state.get_current_room().history == state.narration


@pytest.mark.parametrize("command", ["go forward", "go back"])
def test_going_forward_or_backward_is_refused(game, command):
    before = game.state

    state = game.say(command)

    assert game.room_type == "cave_chamber"
    assert len(state.narration) == 1
    assert "must go either left or right" in game.dm.messages[0]
    assert state.dungeon == before.dungeon
    assert state.player == before.player


def test_player_can_leave_the_chamber_after_being_refused(game):
    game.say("go forward")
    game.say("go left")

    assert game.room_type == "monster_room"


def test_looking_describes_the_chamber_and_keeps_the_player_there(game):
    state = game.say("look around")

    assert game.room_type == "cave_chamber"
    assert len(state.narration) == 1
    assert state.get_current_room().history == state.narration


def test_looking_again_narrates_without_repeating_the_room_history(game):
    first = game.say("look around").narration
    second = game.say("look around").narration

    assert len(second) == 1
    assert game.room_type == "cave_chamber"
    assert game.state.get_current_room().history == first


def test_player_can_leave_the_chamber_after_looking(game):
    game.say("look around")
    game.say("go right")

    assert game.room_type == "monster_room"


def test_player_walks_from_the_cave_entrance_into_the_monster_room():
    game = Scenario(ROUTES)

    game.say("go forward")
    assert game.room_type == "cave_chamber"

    game.say("go left")
    assert game.room_type == "monster_room"

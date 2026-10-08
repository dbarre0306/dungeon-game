"""Commands the router cannot act on, an unknown command or several at once,
are answered in any room and leave the game exactly as it was."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.scenario import Scenario

ROUTES = {
    "dance wildly": RouterState(intent="unknown"),
    "look and go forward": RouterState(intent="multiple"),
    "go forward": RouterState(intent="explore", explore_direction="forward"),
}

ROOMS = [
    pytest.param(0, "cave_entrance", id="cave_entrance"),
    pytest.param(1, "cave_chamber", id="cave_chamber"),
    pytest.param(2, "monster_room", id="monster_room"),
]


@pytest.mark.parametrize(("room_index", "room_type"), ROOMS)
def test_unknown_command_is_narrated_and_nothing_changes(room_index, room_type):
    game = Scenario(ROUTES, room_index=room_index)
    before = game.state

    state = game.say("dance wildly")

    assert game.room_type == room_type
    assert len(state.narration) == 1
    assert "doesn't make any sense" in game.dm.messages[0]
    assert state.dungeon == before.dungeon
    assert state.player == before.player


def test_player_can_carry_on_after_an_unknown_command():
    game = Scenario(ROUTES)

    game.say("dance wildly")
    game.say("go forward")

    assert game.room_type == "cave_chamber"


@pytest.mark.parametrize(("room_index", "room_type"), ROOMS)
def test_multiple_actions_are_refused_and_nothing_changes(room_index, room_type):
    game = Scenario(ROUTES, room_index=room_index)
    before = game.state

    state = game.say("look and go forward")

    assert game.room_type == room_type
    assert state.narration == ["You can only perform one action at a time."]
    assert game.dm.calls == []
    assert state.dungeon == before.dungeon
    assert state.player == before.player


def test_player_can_carry_on_after_a_multiple_action_command():
    game = Scenario(ROUTES)

    game.say("look and go forward")
    game.say("go forward")

    assert game.room_type == "cave_chamber"

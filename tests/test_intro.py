"""The opening of the game: the quest and the starting room are narrated before
the player has typed anything, without consulting the router."""

import pytest

from tests.support.scenario import Scenario


@pytest.fixture
def game() -> Scenario:
    # No routes are scripted, so reaching the router would fail the test.
    scenario = Scenario({})
    scenario.state = scenario.state.model_copy(update={"opening": True})
    return scenario


def test_the_opening_narrates_the_quest_and_the_entrance(game):
    state = game.say("")

    assert game.room_type == "cave_entrance"
    assert len(state.narration) == 1
    assert "Amulet of Valdorin" in game.dm.messages[0]
    assert "troll" in game.dm.messages[0]
    assert "Describe the room" in game.dm.messages[0]


def test_the_opening_is_recorded_in_the_room_history(game):
    state = game.say("")

    assert state.get_current_room().history == state.narration


def test_the_opening_does_not_use_the_player_command(game):
    game.say("")

    assert game.dm.included_command == [False]


def test_the_opening_only_happens_once(game):
    game.say("")

    assert game.state.opening is False

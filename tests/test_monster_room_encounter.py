"""How the monster room behaves around the goblin: the player is held in the room
while it lives and may leave, forward only, once it is dead. Dice only appear to
kill a one-hit-point goblin; combat itself is tested elsewhere."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.builders import goblin, monster_dungeon
from tests.support.fakes import FakeDice
from tests.support.scenario import Scenario

MONSTER_ROOM = 0

ROUTES = {
    "go forward": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "go back": RouterState(intent="explore", explore_direction="backward"),
    "look around": RouterState(intent="look"),
    "attack": RouterState(intent="attack"),
    "buy something": RouterState(intent="shop"),
    "open the chest": RouterState(intent="open_chest"),
}

# A player hit (15 + 3 >= 12) for 6 damage kills a one-hit-point goblin outright.
KILLING_BLOW = (15, 6)


@pytest.fixture
def game() -> Scenario:
    """The player has just reached the monster room, already in a fight; the
    goblin is alive. Its strike is scripted for the tests that provoke it: it
    hits (15 >= 12) for 4, of which the shield absorbs 2."""
    return Scenario(
        ROUTES,
        dungeon=monster_dungeon(),
        room_index=MONSTER_ROOM,
        dice=FakeDice(15, 4),
    )


@pytest.fixture
def cleared() -> Scenario:
    """The player has killed the goblin and is still in the monster room."""
    scenario = Scenario(
        ROUTES,
        dungeon=monster_dungeon(goblin(health_points=1)),
        room_index=MONSTER_ROOM,
        dice=FakeDice(*KILLING_BLOW),
    )
    scenario.say("attack")
    scenario.dm.calls.clear()
    return scenario


def test_looking_describes_the_room_and_keeps_the_player_there(game):
    state = game.say("look around")

    assert game.room_type == "monster_room"
    assert len(state.narration) == 1
    assert state.get_current_room().history == state.narration


@pytest.mark.parametrize("command", ["go forward", "go left", "go back"])
def test_the_goblin_will_not_let_the_player_pass(game, command):
    state = game.say(command)

    assert game.room_type == "monster_room"
    assert len(state.narration) == 2
    assert "will not let them pass" in game.dm.messages[0]
    assert state.get_current_room().enemy.is_alive()


def test_trying_to_leave_costs_the_turn_and_the_goblin_strikes(game):
    state = game.say("go forward")

    assert state.player.health_points == 23
    assert state.player.is_fighting
    game.dice.assert_exhausted()


@pytest.mark.parametrize("command", ["buy something", "open the chest"])
def test_a_command_that_makes_no_sense_in_this_room_is_not_understood(game, command):
    before = game.state

    state = game.say(command)

    assert len(state.narration) == 1
    assert "don't understand" in game.dm.messages[0]
    assert state.dungeon == before.dungeon
    assert state.player == before.player


def test_killing_the_goblin_leaves_the_player_in_the_room():
    game = Scenario(
        ROUTES,
        dungeon=monster_dungeon(goblin(health_points=1)),
        room_index=MONSTER_ROOM,
        dice=FakeDice(*KILLING_BLOW),
    )

    state = game.say("attack")

    assert game.room_type == "monster_room"
    assert state.get_current_room().enemy.is_dead()
    assert state.player.is_alive()
    assert not state.game_over
    assert len(state.narration) == 1
    game.dice.assert_exhausted()  # the dead goblin did not strike back


def test_once_the_goblin_is_dead_the_player_can_go_forward(cleared):
    state = cleared.say("go forward")

    assert cleared.room_type == "cave_chamber"
    assert len(state.narration) == 1
    assert state.get_current_room().history == state.narration


@pytest.mark.parametrize("command", ["go left", "go back"])
def test_once_the_goblin_is_dead_the_only_way_out_is_forward(cleared, command):
    state = cleared.say(command)

    assert cleared.room_type == "monster_room"
    assert len(state.narration) == 1
    assert "only way out is forward" in cleared.dm.messages[0]


def test_attacking_a_dead_goblin_is_refused(cleared):
    before = cleared.state

    state = cleared.say("attack")

    assert len(state.narration) == 1
    assert "already dead" in cleared.dm.messages[0]
    assert state.dungeon == before.dungeon
    assert state.player == before.player
    cleared.dice.assert_exhausted()  # no further rolls were made

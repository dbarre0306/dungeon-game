"""An intent the room does not allow is refused and nothing else happens, even
in a fight. A legal intent that fails during a fight costs the player their turn:
the enemy strikes. Looking, and multiple or unknown commands, never provoke a
strike."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.builders import (
    goblin,
    monster_dungeon,
    shop_dungeon,
    throne_dungeon,
    treasure_dungeon,
)
from tests.support.fakes import FakeDice
from tests.support.scenario import Scenario

ROUTES = {
    "go forward": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "look around": RouterState(intent="look"),
    "attack": RouterState(intent="attack"),
    "buy something": RouterState(intent="shop"),
    "open the left chest": RouterState(intent="open_chest", chest_side="left"),
    "open the right chest": RouterState(intent="open_chest", chest_side="right"),
    "open the chest": RouterState(intent="open_chest"),
    "cast heal": RouterState(intent="cast_healing"),
    "do two things": RouterState(intent="multiple"),
    "dance": RouterState(intent="unknown"),
}

# The enemy hits (a 15 always does) with a damage roll of 4; the shield absorbs 2.
# The goblin and serpent add nothing to it, the troll adds 2.
STRIKE = (15, 4)
PLAYER_HEALTH_POINTS = 30
AFTER_STRIKE = PLAYER_HEALTH_POINTS - 2
AFTER_TROLL_STRIKE = PLAYER_HEALTH_POINTS - 4


def fighting(dungeon, *rolls: int) -> Scenario:
    game = Scenario(ROUTES, dungeon=dungeon, room_index=0, dice=FakeDice(*rolls))
    game.state = game.state.model_copy(
        update={"player": game.state.player.model_copy(update={"is_fighting": True})}
    )
    return game


def monster_fight(*rolls: int) -> Scenario:
    return fighting(monster_dungeon(goblin()), *rolls)


def throne_fight(*rolls: int) -> Scenario:
    return fighting(throne_dungeon(), *rolls)


def serpent_fight(*rolls: int) -> Scenario:
    game = Scenario(
        ROUTES,
        dungeon=treasure_dungeon("right"),
        room_index=0,
        dice=FakeDice(*rolls),
    )
    game.say("open the right chest")
    return game


@pytest.mark.parametrize("command", ["buy something", "open the left chest"])
@pytest.mark.parametrize("make_fight", [monster_fight, throne_fight])
def test_an_illegal_intent_mid_fight_is_refused_without_a_strike(make_fight, command):
    game = make_fight()
    before = game.state

    state = game.say(command)

    assert len(state.narration) == 1
    assert state.dungeon == before.dungeon
    assert state.player == before.player
    game.dice.assert_exhausted()


def test_a_healing_spell_a_warrior_does_not_have_is_illegal_mid_fight():
    game = monster_fight()
    before = game.state

    state = game.say("cast heal")

    assert len(state.narration) == 1
    assert state.player == before.player
    game.dice.assert_exhausted()


def test_attacking_the_peaceful_merchant_is_refused_and_nothing_happens():
    game = Scenario(ROUTES, dungeon=shop_dungeon(), room_index=0)
    before = game.state

    state = game.say("attack")

    assert "merchant is peaceful" in game.dm.messages[0]
    assert state.dungeon == before.dungeon
    assert state.player == before.player


@pytest.mark.parametrize("command", ["look around", "do two things", "dance"])
def test_looking_and_unclear_commands_mid_fight_do_not_provoke_a_strike(command):
    game = monster_fight()

    game.say(command)

    game.dice.assert_exhausted()


@pytest.mark.parametrize("command", ["go forward", "go left"])
@pytest.mark.parametrize(
    ("make_fight", "health_points"),
    [(monster_fight, AFTER_STRIKE), (throne_fight, AFTER_TROLL_STRIKE)],
)
def test_trying_to_leave_mid_fight_costs_the_turn_and_the_enemy_strikes(
    make_fight, health_points, command
):
    game = make_fight(*STRIKE)

    state = game.say(command)

    assert game.room_type in ("monster_room", "throne_room")
    assert len(state.narration) == 2
    assert state.player.health_points == health_points
    assert state.get_current_room().enemy.is_alive()
    game.dice.assert_exhausted()


@pytest.mark.parametrize("command", ["open the left chest", "open the chest"])
def test_a_failed_open_chest_while_the_serpent_is_loose_lets_it_strike(command):
    game = serpent_fight(*STRIKE)

    state = game.say(command)

    assert len(state.narration) == 2
    assert state.player.health_points == AFTER_STRIKE
    game.dice.assert_exhausted()


def test_a_failed_open_chest_before_any_chest_is_opened_costs_nothing():
    game = Scenario(ROUTES, dungeon=treasure_dungeon("right"), room_index=0)
    before = game.state

    state = game.say("open the chest")

    assert len(state.narration) == 1
    assert state.player == before.player

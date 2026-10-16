"""Crossing the trap room. Dice are consumed in order: the d20 to hit (12 or more
strikes), then on a strike a d10 for the wound (8 or more is major: 5 HP, else
minor: 2 HP), then, if the warrior lives, a d3 for the gold (4 to 6 coins)."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.builders import trap_dungeon
from tests.support.fakes import FakeDice
from tests.support.scenario import Scenario

TRAP_ROOM = 0

ROUTES = {
    "cross": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "look around": RouterState(intent="look"),
    "attack": RouterState(intent="attack"),
    "buy something": RouterState(intent="shop"),
    "open the chest": RouterState(intent="open_chest"),
}


def trap(*rolls: int, health_points: int = 20) -> Scenario:
    game = Scenario(
        ROUTES,
        dungeon=trap_dungeon(),
        room_index=TRAP_ROOM,
        dice=FakeDice(*rolls),
    )
    game.state = game.state.model_copy(
        update={
            "player": game.state.player.model_copy(
                update={"health_points": health_points}
            )
        }
    )
    return game


# (rolls, player HP left, gold coins after, wound named in the narration)
CROSSINGS = {
    "dodged, 4 coins": ((5, 1), 20, 14, None),
    "dodged, 6 coins": ((11, 3), 20, 16, None),
    "minor wound": ((12, 7, 2), 18, 15, "minor"),
    "major wound": ((20, 8, 3), 15, 16, "major"),
}


@pytest.mark.parametrize(
    ("rolls", "hp", "gold", "wound"), CROSSINGS.values(), ids=CROSSINGS.keys()
)
def test_crossing_the_room(rolls, hp, gold, wound):
    game = trap(*rolls)

    state = game.say("cross")

    assert state.player.health_points == hp
    assert state.player.gold_coins == gold
    assert state.get_current_room().is_sprung
    assert game.room_type == "trap_room"
    assert not state.game_over
    assert len(state.narration) == 1
    assert "poison dart" in game.dm.messages[0]
    assert (f"{wound} wound" in game.dm.messages[0]) == (wound is not None)
    game.dice.assert_exhausted()


def test_a_fatal_wound_ends_the_game_and_gives_no_gold():
    game = trap(15, 9, health_points=5)

    state = game.say("cross")

    assert state.player.is_dead()
    assert state.player.gold_coins == 10
    assert state.game_over
    assert "killed them" in game.dm.messages[0]
    assert "farewell" in game.dm.messages[1]
    game.dice.assert_exhausted()


def test_once_sprung_the_player_walks_on_without_more_dice():
    game = trap(5, 2)
    game.say("cross")

    game.say("cross")

    assert game.room_type == "cave_chamber"
    game.dice.assert_exhausted()


@pytest.mark.parametrize(
    "command", ["go left", "attack", "buy something", "open the chest"]
)
def test_other_actions_are_refused_without_springing_the_trap(command):
    game = trap()

    state = game.say(command)

    assert not state.get_current_room().is_sprung
    assert state.player.health_points == 20
    assert state.player.gold_coins == 10
    assert game.room_type == "trap_room"


def test_a_sprung_room_has_no_gold_left_to_see():
    game = trap(5, 2)

    state = game.say("cross")

    facts = state.get_current_room().get_room_facts()
    assert any("no gold remains" in fact for fact in facts)

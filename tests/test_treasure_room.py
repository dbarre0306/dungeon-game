"""The treasure room: two chests, one with 3 to 6 gold (2 + a d4) and one with a
15 HP serpent. The player opens exactly one by naming it. The serpent fights like
a monster: the warrior has 20 of 25 HP and +3 to hit (a d20 of 9 or more hits)
with a 2 point shield; the serpent has +0 to hit (12 or more hits)."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.builders import treasure_dungeon
from tests.support.fakes import FakeDice
from tests.support.scenario import Scenario

TREASURE_ROOM = 0

ROUTES = {
    "open the left chest": RouterState(intent="open_chest", chest_side="left"),
    "open the right chest": RouterState(intent="open_chest", chest_side="right"),
    "open the chest": RouterState(intent="open_chest"),
    "go forward": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "attack": RouterState(intent="attack"),
    "drink": RouterState(intent="drink_potion"),
    "look around": RouterState(intent="look"),
    "buy something": RouterState(intent="shop"),
}


def treasure(*rolls: int, serpent_health_points: int = 15) -> Scenario:
    """The serpent is in the right chest and the gold in the left."""
    return Scenario(
        ROUTES,
        dungeon=treasure_dungeon("right", serpent_health_points),
        room_index=TREASURE_ROOM,
        dice=FakeDice(*rolls),
    )


@pytest.mark.parametrize(("roll", "coins"), [(1, 3), (2, 4), (3, 5), (4, 6)])
def test_the_gold_chest_awards_three_to_six_coins_at_once(roll, coins):
    game = treasure(roll)

    state = game.say("open the left chest")

    assert state.player.gold_coins == 10 + coins
    assert state.get_current_room().opened_side == "left"
    assert not state.player.is_fighting
    assert len(state.narration) == 1
    assert f"{coins} gold coins" in game.dm.messages[0]
    game.dice.assert_exhausted()


def test_the_player_can_leave_after_taking_the_gold():
    game = treasure(2)
    game.say("open the left chest")

    game.say("go forward")

    assert game.room_type == "cave_chamber"
    game.dice.assert_exhausted()


def test_the_other_chest_cannot_be_opened_after_the_gold_chest():
    game = treasure(2)
    game.say("open the left chest")
    before = game.state

    state = game.say("open the right chest")

    assert "already opened a chest" in game.dm.messages[-1]
    assert state.player == before.player
    assert state.get_current_room().opened_side == "left"
    game.dice.assert_exhausted()


def test_the_serpent_chest_starts_a_fight_and_tells_the_player_to_kill_it():
    game = treasure()

    state = game.say("open the right chest")

    assert state.player.is_fighting
    assert state.player.health_points == 20
    assert state.player.gold_coins == 10
    assert state.get_current_room().opened_side == "right"
    assert state.get_current_room().enemy.health_points == 15
    assert len(state.narration) == 1
    assert "must kill the serpent" in game.dm.messages[0]


def test_without_naming_a_chest_the_player_is_told_to_say_which():
    game = treasure()
    before = game.state

    state = game.say("open the chest")

    assert len(state.narration) == 1
    assert "must say which chest" in game.dm.messages[0]
    assert state.dungeon == before.dungeon
    assert state.player == before.player


def test_the_serpent_is_not_mentioned_as_a_threat_before_a_chest_is_opened():
    game = treasure()

    facts = game.state.get_current_room().get_room_facts(game.state)

    assert not any("must kill" in fact for fact in facts)


def test_a_fight_round_with_the_serpent():
    game = treasure(15, 4, 14, 5)  # both hit
    game.say("open the right chest")

    state = game.say("attack")

    assert state.get_current_room().enemy.health_points == 11
    assert state.player.health_points == 17
    assert len(state.narration) == 2
    assert game.room_type == "treasure_room"
    game.dice.assert_exhausted()


def test_killing_the_serpent_frees_the_player_without_gold():
    game = treasure(15, 6, serpent_health_points=1)
    game.say("open the right chest")

    state = game.say("attack")

    assert state.get_current_room().enemy.is_dead()
    assert not state.player.is_fighting
    assert state.player.gold_coins == 10
    game.dice.assert_exhausted()  # the dead serpent did not strike back

    game.say("go forward")
    assert game.room_type == "cave_chamber"


def test_the_other_chest_stays_closed_after_the_serpent_is_dead():
    game = treasure(15, 6, serpent_health_points=1)
    game.say("open the right chest")
    game.say("attack")

    state = game.say("open the left chest")

    assert "already opened a chest" in game.dm.messages[-1]
    assert state.player.gold_coins == 10


def test_trying_to_leave_while_the_serpent_lives_costs_a_turn_and_it_strikes():
    game = treasure(15, 5)  # the serpent hits for 5, less 2 from the shield
    game.say("open the right chest")

    state = game.say("go forward")

    assert game.room_type == "treasure_room"
    assert state.player.health_points == 17
    assert (
        state.get_current_room().enemy.health_points == 15
    )  # the player did not attack
    assert len(state.narration) == 2
    assert "lost their turn" in game.dm.messages[-2]
    game.dice.assert_exhausted()


def test_a_serpent_strike_while_leaving_can_kill_the_player():
    game = treasure(15, 6)
    game.say("open the right chest")
    game.state = game.state.model_copy(
        update={"player": game.state.player.model_copy(update={"health_points": 3})}
    )

    state = game.say("go forward")

    assert state.player.is_dead()
    assert state.game_over


def test_going_another_direction_is_refused_without_a_strike():
    game = treasure()
    game.say("open the right chest")

    state = game.say("go left")

    assert "only way out is forward" in game.dm.messages[-1]
    assert state.player.health_points == 20
    game.dice.assert_exhausted()


def test_leaving_before_opening_a_chest_is_refused_without_penalty():
    game = treasure()
    before = game.state

    state = game.say("go forward")

    assert "must open one of the chests" in game.dm.messages[0]
    assert game.room_type == "treasure_room"
    assert state.dungeon == before.dungeon
    assert state.player == before.player


def test_attacking_before_opening_a_chest_is_refused():
    game = treasure()

    game.say("attack")

    assert "nothing here to attack" in game.dm.messages[0]


def test_drinking_a_potion_during_the_fight_lets_the_serpent_strike():
    game = treasure(15, 4)
    game.say("open the right chest")

    state = game.say("drink")

    assert state.player.potions.quantity == 1
    assert state.player.health_points == 23  # healed to 25, then 2 damage
    assert len(state.narration) == 2
    game.dice.assert_exhausted()


def test_a_command_that_makes_no_sense_in_this_room_is_not_understood():
    game = treasure()
    before = game.state

    state = game.say("buy something")

    assert "don't understand" in game.dm.messages[0]
    assert state.player == before.player


def test_looking_during_the_fight_has_the_chests_passageway_and_serpent_to_describe():
    game = treasure()
    game.say("open the right chest")

    facts = " ".join(game.state.get_current_room().get_room_facts(game.state))

    assert "right chest is open" in facts
    assert "left chest is closed" in facts
    assert "passageway" in facts
    assert "serpent" in facts

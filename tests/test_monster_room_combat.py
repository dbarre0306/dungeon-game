"""Fighting the goblin one command at a time. Each attack is the player's strike
followed, if the goblin is still standing, by the goblin's strike back.

The warrior has 20 of 25 HP, +3 to hit (so a d20 roll of 9 or more hits), and a
shield absorbing 2 damage. The goblin has 10 HP and +0 to hit (12 or more hits).
Dice are consumed in order: the player's d20, then d6 for damage on a hit, and
then the same for the goblin."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.fakes import FakeDice
from tests.support.scenario import Scenario

MONSTER_ROOM = 2

ROUTES = {
    "attack": RouterState(intent="attack"),
    "drink": RouterState(intent="drink_potion"),
}

# (rolls, goblin HP left, player HP left)
ROUNDS = {
    "both hit": ((15, 4, 14, 5), 6, 17),
    "player hits, goblin misses": ((15, 4, 5), 6, 20),
    "player misses, goblin hits": ((5, 14, 5), 10, 17),
    "both miss": ((5, 5), 10, 20),
    "player hits on exactly the needed roll": ((9, 4, 11), 6, 20),
    "player misses just under the needed roll": ((8, 12, 5), 10, 17),
    "goblin hits on exactly the needed roll": ((5, 12, 6), 10, 16),
    "goblin misses just under the needed roll": ((15, 1, 11), 9, 20),
    "shield absorbs a weak goblin hit": ((5, 12, 2), 10, 20),
    "shield absorbs all but one point": ((5, 12, 3), 10, 19),
}


def fight(*rolls: int, health_points: int = 20, potions: int = 2) -> Scenario:
    """A fight in the monster room against a full-health goblin, with the dice
    scripted and the warrior's health and potions as given."""
    game = Scenario(ROUTES, room_index=MONSTER_ROOM, dice=FakeDice(*rolls))
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


@pytest.mark.parametrize(
    ("rolls", "goblin_hp", "player_hp"), ROUNDS.values(), ids=ROUNDS.keys()
)
def test_one_round_of_combat(rolls, goblin_hp, player_hp):
    game = fight(*rolls)

    state = game.say("attack")

    assert state.get_current_room().enemy.health_points == goblin_hp
    assert state.player.health_points == player_hp
    assert game.room_type == "monster_room"
    assert not state.game_over
    game.dice.assert_exhausted()


def test_a_round_narrates_both_strikes_and_adds_them_to_the_room_history():
    game = fight(15, 4, 14, 5)

    state = game.say("attack")

    assert len(state.narration) == 2
    assert state.get_current_room().history == state.narration


def test_the_player_is_fighting_once_attacking():
    game = fight(5, 5)
    assert not game.state.player.is_fighting

    state = game.say("attack")

    assert state.player.is_fighting


def test_a_fight_goes_on_over_several_rounds():
    game = fight(15, 4, 5, 15, 4, 5)

    game.say("attack")
    state = game.say("attack")

    assert state.get_current_room().enemy.health_points == 2
    assert state.player.health_points == 20
    game.dice.assert_exhausted()


def test_drinking_a_potion_before_the_fight_heals_and_the_goblin_waits():
    game = fight(health_points=10)  # no dice: the goblin does not strike

    state = game.say("drink")

    assert state.player.health_points == 18
    assert state.player.potions.quantity == 1
    assert not state.player.is_fighting
    assert len(state.narration) == 1


def test_drinking_a_potion_mid_fight_heals_and_the_goblin_strikes():
    game = fight(5, 5, 14, 5, health_points=10)  # a round, then the goblin hits
    game.say("attack")

    state = game.say("drink")

    assert state.player.health_points == 10 + 8 - 3
    assert state.player.potions.quantity == 1
    assert len(state.narration) == 2
    game.dice.assert_exhausted()


def test_a_potion_never_heals_past_full_health():
    game = fight(health_points=22)

    state = game.say("drink")

    assert state.player.health_points == 25
    assert state.player.potions.quantity == 1


def test_a_potion_at_full_health_is_used_up_for_nothing():
    game = fight(health_points=25)

    state = game.say("drink")

    assert state.player.health_points == 25
    assert state.player.potions.quantity == 1
    assert len(state.narration) == 1


def test_with_no_potions_left_nothing_is_healed():
    game = fight(health_points=10, potions=0)

    state = game.say("drink")

    assert state.player.health_points == 10
    assert state.player.potions.quantity == 0
    assert "anymore potions" in game.dm.messages[0]

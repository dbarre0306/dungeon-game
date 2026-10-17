"""Fighting the goblin one command at a time, then in whole fights. Each attack
is the player's strike followed, if the goblin is still standing, by the goblin's
strike back.

The warrior has 20 of 25 HP, +3 to hit (so a d20 roll of 9 or more hits), and a
shield absorbing 2 damage. The goblin has 10 HP and +0 to hit (12 or more hits).
Dice are consumed in order: the player's d20, then d6 for damage on a hit, and
then the same for the goblin."""

import pytest

from tests.support.scenario import fight

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


@pytest.mark.parametrize("damage_roll", [1, 2])
def test_a_hit_absorbed_by_the_shield_is_not_narrated_as_a_wound(damage_roll):
    game = fight(5, 12, damage_roll)  # the player misses, the goblin hits weakly

    state = game.say("attack")

    assert state.player.health_points == 20
    goblin_strike = game.dm.messages[-1]
    assert "took no damage" in goblin_strike
    assert "bronze shield absorbed the blow" in goblin_strike
    assert "Do NOT say the player was wounded" in goblin_strike


def test_a_wound_the_shield_only_partly_absorbed_mentions_the_shield():
    game = fight(5, 12, 5)  # the player misses, the goblin hits for 5: shield blocks 2

    state = game.say("attack")

    assert state.player.health_points == 17
    goblin_strike = game.dm.messages[-1]
    assert "bronze shield absorbed part of the blow" in goblin_strike
    assert "the rest got through" in goblin_strike


def test_a_wound_with_a_broken_shield_does_not_mention_the_shield():
    game = fight(5, 12, 5)
    player = game.state.player
    broken = player.shield.model_copy(update={"durability": 0})  # blocks nothing
    game.state = game.state.model_copy(
        update={"player": player.model_copy(update={"shield": broken})}
    )

    game.say("attack")

    assert "absorbed" not in game.dm.messages[-1]


def test_the_shield_loses_a_durability_point_per_damage_point_it_absorbs():
    game = fight(5, 12, 5)  # the player misses, the goblin hits for 5: shield blocks 2

    state = game.say("attack")

    assert state.player.shield.durability == 4
    assert state.player.shield.condition == "good"


def test_a_hit_the_shield_cannot_fully_absorb_still_wears_it_by_what_it_absorbed():
    game = fight(5, 12, 1)  # the goblin hits for 1: the shield absorbs only 1

    state = game.say("attack")

    assert state.player.shield.durability == 5
    assert state.player.health_points == 20


def test_a_missed_blow_does_not_wear_the_shield():
    game = fight(5, 5)

    state = game.say("attack")

    assert state.player.shield.durability == 6


def test_the_shield_is_damaged_then_broken_and_stops_blocking():
    game = fight(
        5, 12, 6,  # shield 6 -> 4, still good, blocks 2: player 25 -> 21
        5, 12, 6,  # shield 4 -> 2, damaged, narrated: player -> 17
        5, 12, 6,  # damaged shield blocks 1: shield 2 -> 1, player -> 12
        5, 12, 6,  # damaged shield blocks 1: shield 1 -> 0, broken: player -> 7
        5, 12, 6,  # broken shield blocks nothing: player -> 1
        health_points=25,
    )  # fmt: skip

    game.say("attack")
    assert game.state.player.shield.condition == "good"

    state = game.say("attack")
    assert state.player.shield.condition == "damaged"
    assert "bronze shield is now damaged" in game.dm.messages[-1]

    game.say("attack")
    state = game.say("attack")
    assert state.player.shield.condition == "broken"
    assert state.player.get_defense() is None
    assert "bronze shield is now broken" in game.dm.messages[-1]

    health_before = state.player.health_points
    state = game.say("attack")
    assert state.player.health_points == health_before - 6
    assert state.player.shield.durability == 0
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


# Whole fights: every dice roll scripted, from the first blow to the last.


def test_a_flawless_victory():
    game = fight(
        15, 4, 5,  # goblin 10 -> 6, the goblin misses
        15, 4, 5,  # goblin 6 -> 2, the goblin misses
        15, 2,  # goblin 2 -> 0, dead before it can strike
    )  # fmt: skip

    for _ in range(3):
        game.say("attack")
    state = game.say("go forward")

    assert state.player.health_points == 20
    assert game.room_type == "cave_chamber"
    game.dice.assert_exhausted()


def test_killing_the_monster_gives_the_player_its_gold_once():
    game = fight(15, 6, goblin_health_points=5)  # the player kills the goblin

    state = game.say("attack")

    assert state.player.gold_coins == 15  # 10 to start with, plus the room's 5
    assert state.get_current_room().gold_coins == 0
    assert "collected the 5 gold coins" in game.dm.messages[-1]
    game.dice.assert_exhausted()


def test_a_close_win_with_a_potion_mid_fight():
    game = fight(
        15, 3, 14, 6,  # goblin 10 -> 7, the goblin hits for 4: player 6 -> 2
        14, 6,  # potion first: player 2 -> 10, then the goblin hits for 4: -> 6
        15, 6, 14, 4,  # goblin 7 -> 1, the damaged shield blocks 1: player 6 -> 3
        15, 1,  # goblin 1 -> 0, dead
        health_points=6,
    )  # fmt: skip

    game.say("attack")
    game.say("drink")
    game.say("attack")
    state = game.say("attack")

    assert state.get_current_room().enemy.is_dead()
    assert state.player.health_points == 3
    assert state.player.potions.quantity == 1
    assert not state.game_over
    game.dice.assert_exhausted()


def test_a_defeat_ends_the_game_with_a_farewell():
    game = fight(
        5, 14, 6,  # the player misses, the goblin hits for 4: player 6 -> 2
        5, 14, 6,  # the player misses, the goblin hits for 4: player 2 -> 0
        health_points=6,
    )  # fmt: skip

    first = game.say("attack")
    assert first.player.is_alive()
    assert not first.game_over

    state = game.say("attack")

    assert state.player.is_dead()
    assert state.game_over
    assert len(state.narration) == 3  # the player's miss, the killing blow, farewell
    assert "has killed the player" in game.dm.messages[-2]
    assert "farewell" in game.dm.messages[-1]
    game.dice.assert_exhausted()


def test_the_players_blow_lands_before_the_goblins_so_a_double_kill_spares_the_player():
    game = fight(
        15, 6,  # the player kills the goblin, so the goblin never rolls
        health_points=1,
        goblin_health_points=1,
    )  # fmt: skip

    state = game.say("attack")

    assert state.get_current_room().enemy.is_dead()
    assert state.player.health_points == 1
    assert not state.game_over
    game.dice.assert_exhausted()

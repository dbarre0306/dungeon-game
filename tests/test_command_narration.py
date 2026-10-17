"""The player's own words reach the Dungeon Master only when narrating the
player's action, never the enemy's strike back."""

from tests.support.scenario import fight


def test_the_players_strike_includes_the_command_but_the_goblins_does_not():
    game = fight(15, 4, 14, 5)  # both hit

    game.say("attack")

    assert game.dm.included_command == [True, False]


def test_drinking_a_potion_includes_the_command():
    game = fight(5)  # the goblin misses

    game.say("drink")

    assert game.dm.included_command[0] is True

"""The throne room: the player arrives mid-fight with the troll, there is no way
out, and killing the troll wins the game.

The warrior has 20 of 25 HP, +3 to hit (so a d20 roll of 9 or more hits), and a shield
absorbing 2 damage. The troll has 30 HP and +0 to hit (12 or more hits), and
hits for a d10 plus 2. Dice are consumed in order: the player's d20, then d6 for
damage on a hit, and then the troll's d20 and d10 in the same way."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from tests.support.builders import throne_dungeon
from tests.support.fakes import FakeDice
from tests.support.scenario import Scenario

THRONE_ROOM = 0
SHOP_ROOM = 3
PLAYER_HEALTH_POINTS = 20

ROUTES = {
    "go forward": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "go back": RouterState(intent="explore", explore_direction="backward"),
    "look around": RouterState(intent="look"),
    "attack": RouterState(intent="attack"),
    "drink": RouterState(intent="drink_potion"),
    "buy something": RouterState(intent="shop"),
}


def throne_game(*rolls: int, troll_health_points: int = 30) -> Scenario:
    return Scenario(
        ROUTES,
        dungeon=throne_dungeon(troll_health_points),
        room_index=THRONE_ROOM,
        dice=FakeDice(*rolls),
    )


def test_the_factory_builds_a_thirty_hit_point_troll_with_a_spiked_club():
    dungeon = DungeonFactory().generate(merchant=_merchant())

    room = dungeon.rooms[-1]

    assert room.type == "throne_room"
    assert room.enemy.name == "troll"
    assert room.enemy.health_points == 30
    assert "spiked" in room.enemy.weapon
    assert room.enemy.additional_offensive_weapon_damage > 0


def test_leaving_the_shop_puts_the_player_in_the_throne_room_mid_fight():
    game = Scenario(ROUTES, room_index=SHOP_ROOM)

    state = game.say("go forward")

    assert game.room_type == "throne_room"
    assert state.player.is_fighting


def test_the_room_has_a_troll_with_a_club_and_the_amulet_and_no_exit():
    facts = throne_game().state.get_current_room().get_room_facts()

    assert any("troll" in fact and "stone throne" in fact for fact in facts)
    assert any("large spiked wooden club" in fact for fact in facts)
    assert any("Amulet of Valdorin" in fact for fact in facts)
    assert any("no way out" in fact for fact in facts)


@pytest.mark.parametrize("command", ["go forward", "go left", "go back"])
def test_there_is_no_way_out(command):
    game = throne_game()
    before = game.state

    state = game.say(command)

    assert game.room_type == "throne_room"
    assert "no way out" in game.dm.messages[0]
    assert len(state.narration) == 1
    assert state.dungeon == before.dungeon
    assert state.player == before.player
    assert not state.game_over


def test_a_command_that_makes_no_sense_in_this_room_is_not_understood():
    game = throne_game()

    game.say("buy something")

    assert "don't understand" in game.dm.messages[0]


def test_a_round_of_combat_where_both_hit():
    # The player hits for 4; the troll hits for 8 + 2 = 10, the shield absorbs 2.
    game = throne_game(15, 4, 14, 8)

    state = game.say("attack")

    assert state.get_current_room().enemy.health_points == 26
    assert state.player.health_points == PLAYER_HEALTH_POINTS - 8
    assert not state.game_over
    game.dice.assert_exhausted()


def test_the_troll_rolls_a_ten_sided_die_plus_two_for_damage():
    game = throne_game(5, 12, 10)  # the player misses; the troll hits for 10 + 2

    state = game.say("attack")

    assert state.player.health_points == PLAYER_HEALTH_POINTS - (12 - 2)


def test_the_troll_misses_just_under_the_needed_roll():
    game = throne_game(5, 11)

    state = game.say("attack")

    assert state.player.health_points == PLAYER_HEALTH_POINTS
    game.dice.assert_exhausted()


def test_drinking_a_potion_mid_fight_heals_and_lets_the_troll_strike():
    # The player misses and the troll hits for 5 + 2 - 2; then the potion heals 8
    # and the troll hits for 5 again.
    game = throne_game(5, 14, 5, 14, 5)
    game.say("attack")

    state = game.say("drink")

    assert state.player.potions.quantity == 1
    assert state.player.health_points == (PLAYER_HEALTH_POINTS - 5) + 8 - 5


def test_killing_the_troll_wins_the_game():
    game = throne_game(15, 6, troll_health_points=1)  # no troll strike follows

    state = game.say("attack")

    assert state.get_current_room().enemy.is_dead()
    assert state.game_over
    assert state.player.health_points == PLAYER_HEALTH_POINTS
    game.dice.assert_exhausted()


def test_the_win_narrates_the_amulet_taken_from_the_neck_and_the_kingdom():
    game = throne_game(15, 6, troll_health_points=1)

    state = game.say("attack")

    assert len(state.narration) == 2
    kill, victory = game.dm.messages
    assert "Do NOT say anything about a way out" in kill
    assert "Amulet of Valdorin" in victory
    assert "neck" in victory
    assert "kingdom" in victory


def test_the_troll_is_not_finished_while_it_has_hit_points_left():
    game = throne_game(15, 6, 5, troll_health_points=7)

    state = game.say("attack")

    assert state.get_current_room().enemy.health_points == 1
    assert not state.game_over


def test_the_troll_killing_the_player_ends_the_game():
    game = throne_game(5, 14, 10, 5)
    player = game.state.player
    game.state = game.state.model_copy(
        update={"player": player.model_copy(update={"health_points": 5})}
    )

    state = game.say("attack")

    assert state.player.is_dead()
    assert state.game_over
    assert "farewell" in game.dm.messages[-1]


def _merchant() -> Merchant:
    return Merchant(merchandise=create_default_warrior().get_supported_merchandise())

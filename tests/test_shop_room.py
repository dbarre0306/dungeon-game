"""The shop room: the merchant, who lives in the game state, sells a warrior
three potions (5 gold each), one steel sword and one steel shield (10 gold
each). Whatever is sold leaves the merchant's stock. The default warrior starts
with 10 gold, 2 potions, a bronze sword (+0 damage) and a bronze shield (2
damage reduction)."""

import pytest

from dungeon_game.agents.router_agent import RouterState
from tests.support.builders import shop_dungeon
from tests.support.scenario import Scenario

SHOP_ROOM = 0

ROUTES = {
    "buy a potion": RouterState(intent="shop", shop_item_name="potion"),
    "buy the sword": RouterState(intent="shop", shop_item_name="sword"),
    "buy the shield": RouterState(intent="shop", shop_item_name="shield"),
    "buy something": RouterState(intent="shop"),
    "buy 2 potions": RouterState(
        intent="shop", shop_item_name="potion", shop_quantity=2
    ),
    "buy 3 potions": RouterState(
        intent="shop", shop_item_name="potion", shop_quantity=3
    ),
    "buy 4 potions": RouterState(
        intent="shop", shop_item_name="potion", shop_quantity=4
    ),
    "buy 0 potions": RouterState(
        intent="shop", shop_item_name="potion", shop_quantity=0
    ),
    "buy -1 potions": RouterState(
        intent="shop", shop_item_name="potion", shop_quantity=-1
    ),
    "buy 2 swords": RouterState(intent="shop", shop_item_name="sword", shop_quantity=2),
    "go forward": RouterState(intent="explore", explore_direction="forward"),
    "go left": RouterState(intent="explore", explore_direction="left"),
    "attack": RouterState(intent="attack"),
}


def shop(gold_coins: int = 10) -> Scenario:
    game = Scenario(ROUTES, dungeon=shop_dungeon(), room_index=SHOP_ROOM)
    player = game.state.player.model_copy(update={"gold_coins": gold_coins})
    game.state = game.state.model_copy(update={"player": player})
    return game


def in_stock(state, item: str) -> int:
    return state.get_current_room().merchant.quantity_of(item)


def test_a_potion_costs_five_gold_and_can_be_bought_repeatedly():
    game = shop(gold_coins=10)

    game.say("buy a potion")
    state = game.say("buy a potion")

    assert state.player.gold_coins == 0
    assert state.player.potions.quantity == 4
    assert in_stock(state, "potion") == 1
    assert "5 gold coins" in game.dm.messages[-1]


def test_the_merchant_has_three_potions_and_then_sells_out():
    game = shop(gold_coins=20)

    for _ in range(3):
        game.say("buy a potion")
    state = game.say("buy a potion")

    assert state.player.potions.quantity == 5
    assert state.player.gold_coins == 5
    assert in_stock(state, "potion") == 0
    assert "none of that" in game.dm.messages[-1]


def test_a_potion_cannot_be_bought_without_enough_gold():
    game = shop(gold_coins=4)

    state = game.say("buy a potion")

    assert state.player.gold_coins == 4
    assert state.player.potions.quantity == 2
    assert in_stock(state, "potion") == 3
    assert "cannot afford" in game.dm.messages[-1]


def test_the_warrior_buys_a_steel_sword_for_ten_gold():
    game = shop(gold_coins=10)

    state = game.say("buy the sword")

    assert state.player.gold_coins == 0
    assert state.player.offensive_weapon == "steel sword"
    assert state.player.additional_offensive_weapon_damage == 2
    assert in_stock(state, "sword") == 0


def test_the_warrior_buys_a_steel_shield_for_ten_gold():
    game = shop(gold_coins=10)

    state = game.say("buy the shield")

    assert state.player.gold_coins == 0
    assert state.player.defensive_weapon == "steel shield"
    assert state.player.reduced_defensive_weapon_damage == 4
    assert in_stock(state, "shield") == 0


def test_the_merchant_has_only_one_sword_to_sell():
    game = shop(gold_coins=20)
    game.say("buy the sword")

    state = game.say("buy the sword")

    assert state.player.gold_coins == 10
    assert "none of that" in game.dm.messages[-1]


def test_an_upgrade_cannot_be_bought_without_enough_gold():
    game = shop(gold_coins=9)

    state = game.say("buy the sword")

    assert state.player.gold_coins == 9
    assert state.player.offensive_weapon == "bronze sword"
    assert in_stock(state, "sword") == 1
    assert "cannot afford" in game.dm.messages[-1]


def test_the_player_must_say_what_to_buy():
    game = shop()

    state = game.say("buy something")

    assert state.player.gold_coins == 10
    assert "what they want to buy" in game.dm.messages[-1]


def test_several_potions_can_be_bought_at_once():
    game = shop(gold_coins=10)

    state = game.say("buy 2 potions")

    assert state.player.gold_coins == 0
    assert state.player.potions.quantity == 4
    assert in_stock(state, "potion") == 1
    assert "bought 2" in game.dm.messages[-1]
    assert "10 gold coins" in game.dm.messages[-1]


def test_more_potions_than_the_merchant_has_cannot_be_bought():
    game = shop(gold_coins=100)

    state = game.say("buy 4 potions")

    assert state.player.gold_coins == 100
    assert state.player.potions.quantity == 2
    assert in_stock(state, "potion") == 3
    assert "only has 3 of potion left" in game.dm.messages[-1]


def test_several_potions_cannot_be_bought_without_enough_gold():
    game = shop(gold_coins=7)

    state = game.say("buy 2 potions")

    assert state.player.gold_coins == 7
    assert state.player.potions.quantity == 2
    assert in_stock(state, "potion") == 3
    assert "cost 10 gold coins" in game.dm.messages[-1]


@pytest.mark.parametrize("command", ["buy 0 potions", "buy -1 potions"])
def test_at_least_one_item_must_be_bought(command):
    game = shop(gold_coins=10)

    state = game.say(command)

    assert state.player.gold_coins == 10
    assert state.player.potions.quantity == 2
    assert "at least one" in game.dm.messages[-1]


def test_several_of_a_single_item_cannot_be_bought():
    game = shop(gold_coins=100)

    state = game.say("buy 2 swords")

    assert state.player.gold_coins == 100
    assert state.player.offensive_weapon == "bronze sword"
    assert in_stock(state, "sword") == 1
    assert "only has 1 of steel sword left" in game.dm.messages[-1]


def test_the_player_can_leave_forward_with_or_without_buying():
    game = shop()

    game.say("go forward")

    assert game.room_type == "cave_chamber"


def test_the_player_cannot_leave_any_other_way():
    game = shop()

    game.say("go left")

    assert game.room_type == "shop_room"
    assert "only way out is forward" in game.dm.messages[-1]


def test_there_is_nothing_to_attack():
    game = shop()

    state = game.say("attack")

    assert not state.player.is_fighting
    assert "nothing here to attack" in game.dm.messages[-1]


@pytest.mark.parametrize("command", ["buy a potion", "buy the sword"])
def test_a_purchase_is_recorded_in_the_room_history(command):
    game = shop()

    state = game.say(command)

    assert state.get_current_room().history == state.narration


def shop_facts(game: Scenario) -> str:
    return " ".join(game.state.get_current_room().get_room_facts())


def test_the_room_facts_list_what_is_for_sale_with_prices():
    game = shop(gold_coins=7)

    facts = shop_facts(game)

    assert "3 of potion at a price of 5 gold coins each" in facts
    assert "one steel sword at a price of 10 gold coins" in facts
    assert "one steel shield at a price of 10 gold coins" in facts
    assert "does not have to buy anything" in facts
    assert "sold out" not in facts


def test_the_room_facts_drop_what_has_been_bought_out():
    game = shop(gold_coins=20)
    game.say("buy the sword")
    game.say("buy 2 potions")

    facts = shop_facts(game)

    assert "steel sword" not in facts
    assert "one potion at a price of 5 gold coins" in facts
    assert "one steel shield at a price of 10 gold coins" in facts


def test_the_room_facts_say_so_when_the_merchant_has_nothing_left():
    game = shop(gold_coins=100)
    game.say("buy the sword")
    game.say("buy the shield")
    game.say("buy 3 potions")

    facts = shop_facts(game)

    assert "out of items to sell" in facts
    assert "at a price of" not in facts


def test_the_purchase_is_narrated_with_the_updated_player_and_merchant():
    game = shop(gold_coins=10)

    game.say("buy the sword")

    narrated_state, _ = game.dm.calls[-1]
    assert narrated_state.player.gold_coins == 0
    assert narrated_state.get_current_room().merchant.quantity_of("sword") == 0

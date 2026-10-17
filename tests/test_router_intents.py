"""The router only offers a player the actions its class can take, and turns
anything else the model returns into an unknown command."""

from types import SimpleNamespace

from dungeon_game.agents.router_agent import RouterAgent, RouterState
from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.actors.player.mage import (
    FireBoltSpell,
    HealingSpell,
    Mage,
    Staff,
)
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.nodes.router import RouterNode
from tests.support.builders import full_dungeon, new_game_state
from tests.support.fakes import FakeRouterAgent


def _mage() -> Mage:
    return Mage(
        max_health_points=15,
        health_points=15,
        gold_coins=0,
        hit_bonus=2,
        current_room_index=0,
        staff=Staff(
            name="wooden staff",
            fire_bolt_spell=FireBoltSpell(name="firebolt", additional_damage_points=2),
            healing_spell=HealingSpell(name="mend", health_points=5, quantity=1),
        ),
    )


def _agent_returning(router_state: RouterState) -> RouterAgent:
    agent = RouterAgent.__new__(RouterAgent)
    agent._agent = SimpleNamespace(
        invoke=lambda _: {"structured_response": router_state}
    )
    return agent


def _prompt_for(player) -> str:
    fake = FakeRouterAgent({"drink a potion": RouterState(intent="unknown")})
    state = new_game_state(player, full_dungeon(), command="drink a potion")
    RouterNode(fake).execute(state)  # type: ignore[arg-type]
    return fake.prompts[0]


def test_warrior_supports_drinking_potions():
    assert "drink_potion" in create_default_warrior().get_supported_intents()


def test_mage_does_not_support_drinking_potions():
    assert "drink_potion" not in _mage().get_supported_intents()


def test_warrior_prompt_offers_drink_potion():
    assert "`drink_potion`" in _prompt_for(create_default_warrior())


def test_mage_prompt_does_not_offer_drink_potion():
    prompt = _prompt_for(_mage())
    assert "drink_potion" not in prompt
    assert "`attack`" in prompt


def test_prompt_always_offers_multiple_and_unknown():
    prompt = _prompt_for(_mage())
    assert "`multiple`" in prompt
    assert "`unknown`" in prompt


def test_supported_intent_passes_through():
    agent = _agent_returning(RouterState(intent="attack"))
    assert agent.invoke("hit it", ["attack", "look"], []).intent == "attack"


def test_multiple_and_unknown_pass_through_whatever_the_player_supports():
    for intent in ("multiple", "unknown"):
        agent = _agent_returning(RouterState(intent=intent))
        assert agent.invoke("???", [], []).intent == intent


def test_unsupported_intent_becomes_unknown_and_drops_its_fields():
    agent = _agent_returning(
        RouterState(intent="shop", shop_item_name="potion", shop_quantity=2)
    )

    result = agent.invoke("buy potions", ["attack"], ["potion"])

    assert result == RouterState(intent="unknown")


def test_warrior_sells_potion_sword_and_shield():
    sold = [m.type for m in create_default_warrior().get_supported_merchandise()]
    assert sold == ["potion", "sword", "shield"]


def test_mage_sells_only_an_elder_staff_for_ten_gold():
    (merchandise,) = _mage().get_supported_merchandise()
    assert merchandise.type == "elder_staff"
    assert merchandise.name == "elder staff"
    assert merchandise.price == 10


def test_merchant_stocks_what_the_player_can_buy():
    merchant = Merchant(merchandise=_mage().get_supported_merchandise())
    assert merchant.is_in_stock("elder_staff", 1)
    assert not merchant.is_in_stock("sword", 1)


def test_mage_prompt_offers_only_the_elder_staff_to_buy():
    fake = FakeRouterAgent({"buy it": RouterState(intent="unknown")})
    RouterNode(fake).execute(  # type: ignore[arg-type]
        new_game_state(_mage(), full_dungeon(), command="buy it")
    )
    prompt = fake.prompts[0]
    assert "`elder_staff`" in prompt
    assert "`sword`" not in prompt
    assert "`shield`" not in prompt


def test_warrior_prompt_offers_potion_sword_and_shield_to_buy():
    prompt = _prompt_for(create_default_warrior())
    assert "`potion`, `sword`, `shield`" in prompt
    assert "elder_staff" not in prompt


def test_shop_item_the_player_cannot_buy_is_cleared():
    agent = _agent_returning(
        RouterState(intent="shop", shop_item_name="sword", shop_quantity=1)
    )

    result = agent.invoke("buy a sword", ["shop"], ["elder_staff"])

    assert result == RouterState(intent="shop", shop_quantity=1)


def test_shop_item_the_player_can_buy_passes_through():
    state = RouterState(intent="shop", shop_item_name="elder_staff")
    agent = _agent_returning(state)

    assert agent.invoke("buy staff", ["shop"], ["elder_staff"]) == state

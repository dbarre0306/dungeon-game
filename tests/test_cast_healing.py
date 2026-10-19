"""A mage's healing spell restores full health and has a limited number of casts."""

from dungeon_game.agents.router_agent import RouterState
from dungeon_game.domain.actors.player.mage import Mage, create_default_mage
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.items.inventory_items import ELDER_STAFF
from dungeon_game.domain.rooms.cave_chamber import CaveChamber
from dungeon_game.game_graph import GameGraph
from dungeon_game.game_state import GameState
from tests.support.builders import goblin, monster_dungeon, trap_dungeon
from tests.support.fakes import FakeDice, FakeDungeonMaster, FakeRouterAgent

ROUTES = {"heal": RouterState(intent="cast_healing")}


def _mage(health_points: int = 10, casts: int = 1, is_fighting: bool = False) -> Mage:
    mage = create_default_mage()
    assert isinstance(mage, Mage)
    healing = mage.staff.healing_spell.model_copy(update={"quantity": casts})
    return mage.model_copy(
        update={
            "health_points": health_points,
            "is_fighting": is_fighting,
            "staff": mage.staff.model_copy(update={"healing_spell": healing}),
        }
    )


def _cast(player: Mage, dungeon, dice: FakeDice | None = None):
    dm = FakeDungeonMaster()
    graph = GameGraph(FakeRouterAgent(ROUTES), dm, dice or FakeDice())
    state = graph.invoke(GameState(player=player, dungeon=dungeon, command="heal"))
    return state, dm


def test_healing_restores_full_health_and_spends_a_cast():
    state, dm = _cast(_mage(health_points=5, casts=2), trap_dungeon())

    assert state.player.health_points == state.player.max_health_points
    assert state.player.staff.healing_spell.quantity == 1
    assert "restored to full strength" in dm.messages[-1]


def test_healing_at_full_health_is_still_spent():
    mage = _mage(casts=2)
    mage = mage.model_copy(update={"health_points": mage.max_health_points})

    state, dm = _cast(mage, trap_dungeon())

    assert state.player.staff.healing_spell.quantity == 1
    assert "already at full strength" in dm.messages[-1]


def test_healing_with_no_casts_left_changes_nothing():
    state, dm = _cast(_mage(health_points=5, casts=0), trap_dungeon())

    assert state.player.health_points == 5
    assert state.player.staff.healing_spell.quantity == 0
    assert "can't cast the healing spell anymore" in dm.messages[-1]


def test_healing_during_a_fight_costs_a_turn():
    mage = _mage(health_points=5, is_fighting=True)
    dungeon = monster_dungeon(goblin())

    # One roll: the goblin's attack roll misses.
    dice = FakeDice(1)
    state, dm = _cast(mage, dungeon, dice)

    assert state.player.staff.healing_spell.quantity == 0
    assert any("goblin attacked" in msg for msg in dm.messages)
    dice.assert_exhausted()


def test_buying_a_staff_keeps_the_healing_casts_left():
    mage = _mage(casts=1)

    upgraded = mage.with_purchased_item(ELDER_STAFF, 1, 0)

    assert upgraded.staff.name == "elder staff"
    assert upgraded.staff.healing_spell.quantity == 3


def test_healing_works_in_a_room_that_rejects_other_actions():
    dungeon = Dungeon(rooms=[CaveChamber()])

    state, dm = _cast(_mage(health_points=5, casts=1), dungeon)

    assert state.player.health_points == state.player.max_health_points
    assert state.player.staff.healing_spell.quantity == 0
    assert "restored to full strength" in dm.messages[-1]


def test_facts_offer_healing_only_while_casts_remain():
    with_casts = " ".join(_mage(casts=2).get_facts())
    without_casts = " ".join(_mage(casts=0).get_facts())

    assert "can cast a healing spell" in with_casts
    assert "2 more times" in with_casts
    assert "can cast a healing spell" not in without_casts
    assert "no healing spell casts left" in without_casts

"""Each room has a set of legal intents, limited to what the player's class can
do."""

import pytest

from dungeon_game.domain.actors.player.mage import create_default_mage
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon import Dungeon
from tests.support.builders import (
    full_dungeon,
    monster_dungeon,
    shop_dungeon,
    throne_dungeon,
    trap_dungeon,
    treasure_dungeon,
)

WARRIOR = create_default_warrior()
MAGE = create_default_mage()


def _room(dungeon: Dungeon, room_type: str):
    return next(room for room in dungeon.rooms if room.type == room_type)


ROOMS = {
    "cave_entrance": _room(full_dungeon(), "cave_entrance"),
    "cave_chamber": _room(full_dungeon(), "cave_chamber"),
    "monster_room": _room(monster_dungeon(), "monster_room"),
    "trap_room": _room(trap_dungeon(), "trap_room"),
    "treasure_room": _room(treasure_dungeon(), "treasure_room"),
    "shop_room": _room(shop_dungeon(), "shop_room"),
    "throne_room": _room(throne_dungeon(), "throne_room"),
}

# The doc's table, with heal split into the warrior's and the mage's intent.
ROOM_INTENTS = {
    "cave_entrance": {"look", "explore"},
    "cave_chamber": {"look", "explore"},
    "monster_room": {"look", "explore", "attack"},
    "trap_room": {"look", "explore"},
    "treasure_room": {"look", "explore", "attack", "open_chest"},
    "shop_room": {"look", "explore", "shop"},
    "throne_room": {"look", "explore", "attack"},
}


@pytest.mark.parametrize("room_type", ROOM_INTENTS)
def test_warrior_legal_intents(room_type):
    legal = ROOMS[room_type].get_legal_intents(WARRIOR)

    assert legal == ROOM_INTENTS[room_type] | {"drink_potion"}


@pytest.mark.parametrize("room_type", ROOM_INTENTS)
def test_mage_legal_intents(room_type):
    legal = ROOMS[room_type].get_legal_intents(MAGE)

    assert legal == ROOM_INTENTS[room_type] | {"cast_healing"}


@pytest.mark.parametrize("player", [WARRIOR, MAGE], ids=lambda p: p.type)
@pytest.mark.parametrize("room_type", ROOM_INTENTS)
def test_multiple_and_unknown_are_never_legal(room_type, player):
    legal = ROOMS[room_type].get_legal_intents(player)

    assert not legal & {"multiple", "unknown"}

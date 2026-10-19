"""Drinking a potion and casting a healing spell are allowed in every room,
including ones that refuse most other actions."""

import pytest

from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from tests.support.builders import full_dungeon, trap_dungeon, treasure_dungeon

ROOMS: list[DungeonRoom] = [
    *full_dungeon().rooms,
    *trap_dungeon().rooms[:1],
    *treasure_dungeon().rooms[:1],
]


@pytest.mark.parametrize("room", ROOMS, ids=lambda room: room.type)
@pytest.mark.parametrize("intent_type", ["drink_potion", "cast_healing"])
def test_room_allows_healing_actions(room, intent_type):
    assert room.is_valid_intent(Intent(type=intent_type)) == (True, None)

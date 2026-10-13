from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.game_state import GameState


def test_room_facts_name_the_enemy_and_its_weapon():
    enemy = Enemy(
        name="rat",
        weapon="razor sharp teeth",
        max_health_points=10,
        health_points=10,
        hit_bonus=0,
    )
    room = MonsterRoom(enemy=enemy)
    state = GameState(
        player=create_default_warrior(), dungeon=Dungeon(rooms=[room]), command=""
    )
    facts = room.get_room_facts(state)
    assert (
        "The rat, armed with razor sharp teeth, is in this room "
        "and is itching for a fight." in facts
    )
    assert not any("bound method" in fact for fact in facts)

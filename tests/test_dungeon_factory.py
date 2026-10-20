"""The stats of the enemies the factory builds, and the heroes' starting stats."""

import pytest

from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.actors.player.mage import create_default_mage
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory

# name: (HP, to-hit bonus, damage die sides, damage bonus)
ENEMIES = {
    "giant rat": (7, 2, 3, 0),
    "goblin": (10, 3, 4, 1),
    "orc": (16, 4, 6, 1),
    "serpent": (12, 3, 6, 0),
    "troll": (30, 4, 8, 2),
}


def _enemies() -> dict:
    merchant = Merchant(
        merchandise=create_default_warrior().get_supported_merchandise()
    )
    enemies = {}
    for _ in range(200):
        for room in DungeonFactory().generate(merchant).rooms:
            if hasattr(room, "enemy"):
                enemies[room.enemy.name] = room.enemy
    return enemies


@pytest.mark.parametrize("name", ENEMIES)
def test_each_enemy_has_its_designed_stats(name):
    enemy = _enemies()[name]

    health, hit_bonus, die, bonus = ENEMIES[name]
    assert enemy.max_health_points == enemy.health_points == health
    assert enemy.hit_bonus == hit_bonus
    assert enemy.damage_die == die
    assert enemy.additional_offensive_weapon_damage == bonus


def test_the_warrior_starts_with_thirty_hit_points_and_plus_three_to_hit():
    warrior = create_default_warrior()

    assert warrior.max_health_points == warrior.health_points == 30
    assert warrior.hit_bonus == 3


def test_the_mage_starts_with_eighteen_hit_points_and_plus_four_to_hit():
    mage = create_default_mage()

    assert mage.max_health_points == mage.health_points == 18
    assert mage.hit_bonus == 4

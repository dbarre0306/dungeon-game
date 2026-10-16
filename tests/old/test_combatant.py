from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.player.mage import (
    FireBoltSpell,
    HealingSpell,
    Mage,
    Staff,
)
from dungeon_game.domain.actors.player.warrior import Sword, create_default_warrior


def _mage() -> Mage:
    return Mage(
        max_health_points=15,
        health_points=15,
        is_fighting=False,
        gold_coins=0,
        hit_bonus=2,
        current_room_index=0,
        staff=Staff(
            name="wooden staff",
            fire_bolt_spell=FireBoltSpell(name="firebolt", additional_damage_points=2),
            healing_spell=HealingSpell(name="mend", health_points=5, quantity=1),
        ),
    )


def test_warrior_attacks_with_its_sword():
    warrior = create_default_warrior()
    assert warrior.get_weapon() == "bronze sword"
    assert warrior.get_attack() == "bronze sword"


def test_mage_carries_a_staff_but_attacks_with_firebolt():
    mage = _mage()
    assert mage.get_weapon() == "wooden staff"
    assert mage.get_attack() == "firebolt"


def test_enemy_attacks_with_its_weapon():
    enemy = Enemy(
        name="orc",
        weapon="battle ax",
        max_health_points=10,
        health_points=10,
        hit_bonus=0,
    )
    assert enemy.get_weapon() == "battle ax"
    assert enemy.get_attack() == "battle ax"


def test_warrior_facts_name_the_current_equipment():
    warrior = create_default_warrior()
    assert (
        warrior.get_facts()
        == "The player is a warrior with a bronze sword and a bronze shield."
    )

    steel_sword = Sword(name="steel sword", additional_damage_points=2)
    upgraded = warrior.model_copy(update={"sword": steel_sword})
    assert "steel sword" in upgraded.get_facts()
    assert "bronze sword" not in upgraded.get_facts()


def test_mage_facts_name_the_staff():
    assert _mage().get_facts() == "The player is a mage with a wooden staff."

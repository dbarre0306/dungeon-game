from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.player.mage import Mage
from dungeon_game.domain.actors.player.warrior import Sword, create_default_warrior
from dungeon_game.domain.items.inventory_items import (
    FireBoltSpell,
    HealingSpell,
    Staff,
)


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
    assert warrior.offensive_weapon == "bronze sword"
    assert warrior.offensive_weapon_payload == "bronze sword"


def test_mage_carries_a_staff_but_attacks_with_firebolt():
    mage = _mage()
    assert mage.offensive_weapon == "wooden staff"
    assert mage.offensive_weapon_payload == "firebolt"


def test_enemy_attacks_with_its_weapon():
    enemy = Enemy(
        name="orc",
        weapon="battle ax",
        max_health_points=10,
        health_points=10,
        hit_bonus=0,
    )
    assert enemy.offensive_weapon == "battle ax"
    assert enemy.offensive_weapon_payload == "battle ax"


def test_warrior_facts_name_the_current_equipment():
    warrior = create_default_warrior()
    facts = warrior.get_facts()
    assert "The player is a warrior." in facts
    assert "The player has a bronze sword." in facts
    assert "The player has a bronze shield." in facts
    assert "The player has 2 potion bottles." in facts

    steel_sword = Sword(name="steel sword", additional_damage_points=2)
    upgraded = warrior.model_copy(update={"sword": steel_sword})
    assert "The player has a steel sword." in upgraded.get_facts()
    assert "The player has a bronze sword." not in upgraded.get_facts()


def test_mage_facts_name_the_staff():
    facts = _mage().get_facts()
    assert "The player has a wooden staff." in facts

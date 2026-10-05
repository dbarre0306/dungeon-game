from typing import Literal

from pydantic import BaseModel

from dungeon_game.domain.player.player import Player


class FireBoltSpell(BaseModel):
    name: str
    additional_damage_points: int


class HealingSpell(BaseModel):
    name: str
    health_points: int
    quantity: int


class Staff(BaseModel):
    name: str
    fire_bolt_spell: FireBoltSpell
    healing_spell: HealingSpell


class Mage(Player):
    type: Literal["mage"] = "mage"
    staff: Staff

    def get_facts(self) -> str:
        return "The player is a mage with a magical staff."

    def get_weapon(self) -> str:
        return "firebolt"

    def get_extra_weapon_damage(self) -> int:
        return self.staff.fire_bolt_spell.additional_damage_points

    def get_damage_reduction(self) -> int:
        return 0

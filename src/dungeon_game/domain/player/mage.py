from typing import Literal

from pydantic import BaseModel

from dungeon_game.domain.player.player import Player


class Staff(BaseModel):
    name: str

    def __init__(self, name: str):
        super().__init__(name=name)


class FireBoltSpell(BaseModel):
    name: str
    additional_damage_points: int


class HealingSpell(BaseModel):
    name: str
    health_points: int
    quantity: int


class Mage(Player):
    type: Literal["mage"] = "mage"
    staff: Staff
    fire_bolt_spell: FireBoltSpell
    healing_spell: HealingSpell

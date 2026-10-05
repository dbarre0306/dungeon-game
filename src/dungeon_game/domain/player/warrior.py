from typing import Literal

from pydantic import BaseModel

from dungeon_game.domain.player.player import Player, Potions


class Sword(BaseModel):
    name: str
    additional_damage_points: int

    def __init__(self, name: str, additional_damage_points: int):
        super().__init__(name=name, additional_damage_points=additional_damage_points)


class Shield(BaseModel):
    name: str
    defensive_health_points: int
    # TODO: support condition (good, damaged, broken)

    def __init__(self, name: str, defensive_health_points: int):
        super().__init__(name=name, defensive_health_points=defensive_health_points)


class Warrior(Player):
    type: Literal["warrior"] = "warrior"
    sword: Sword
    shield: Shield

    def get_facts(self) -> str:
        return "The player is a warrior with a sword and a shield."

    def get_weapon(self) -> str:
        return self.sword.name

    def get_extra_weapon_damage(self) -> int:
        return self.sword.additional_damage_points

    def get_damage_reduction(self) -> int:
        return self.shield.defensive_health_points


def create_default_warrior() -> Player:
    return Warrior(
        max_health_points=25,
        health_points=20,
        is_fighting=False,
        potions=Potions(health_points=8, quantity=2),
        sword=Sword("bronze sword", 0),
        shield=Shield("bronze shield", 2),
        gold_coins=10,
        hit_bonus=3,
        current_room_index=0,
    )

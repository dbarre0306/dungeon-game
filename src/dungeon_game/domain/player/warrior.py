from typing import Literal

from pydantic import BaseModel

from dungeon_game.domain.player.player import Player


class Sword(BaseModel):
    name: str
    additional_damage_points: int

    def __init__(self, name: str, additional_damage_points: int):
        super().__init__(name=name, additional_damage_points=additional_damage_points)


class Shield(BaseModel):
    name: str
    defensive_health_points: int

    def __init__(self, name: str, defensive_health_points: int):
        super().__init__(name=name, defensive_health_points=defensive_health_points)


class Warrior(Player):
    type: Literal["warrior"] = "warrior"
    sword: Sword
    shield: Shield

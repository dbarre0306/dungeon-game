from typing import Literal

from pydantic import BaseModel

from dungeon_game.domain.actors.player.player import Player, Potions


class Sword(BaseModel):
    name: str
    additional_damage_points: int


class Shield(BaseModel):
    name: str
    defensive_health_points: int
    # TODO: support condition (good, damaged, broken)


class Warrior(Player):
    type: Literal["warrior"] = "warrior"
    sword: Sword
    shield: Shield

    def get_facts(self) -> str:
        return (
            f"The player is a warrior with a {self.sword.name} "
            f"and a {self.shield.name}."
        )

    def get_weapon(self) -> str:
        return self.sword.name

    def get_extra_damage(self) -> int:
        return self.sword.additional_damage_points

    def get_defense(self) -> str | None:
        return self.shield.name

    def get_damage_reduction(self) -> int:
        return self.shield.defensive_health_points


def create_default_warrior() -> Player:
    return Warrior(
        max_health_points=25,
        health_points=20,
        is_fighting=False,
        potions=Potions(health_points=8, quantity=2),
        sword=Sword(name="bronze sword", additional_damage_points=0),
        shield=Shield(name="bronze shield", defensive_health_points=2),
        gold_coins=10,
        hit_bonus=3,
        current_room_index=0,
    )

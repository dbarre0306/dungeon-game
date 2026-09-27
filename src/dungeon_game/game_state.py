from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel, Field

ActionType = Literal[
    "explore", "combat", "shop", "drink_potion", "open_chest", "multiple", "unknown"
]
ExploreOption = Literal["left", "right", "forward", "backward", "look"]

WeaponCondition = Literal["good", "cracked", "broken"]


class Action(BaseModel):
    action: ActionType | None = None
    explore_option: ExploreOption | None = None


class DungeonRoom(BaseModel):
    id: str
    initial_facts: list[str]
    events: list[str]
    next_room: DungeonRoom | None


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


class Potions(BaseModel):
    name: str
    health_points: int
    quantity: int

    def __init__(self, health_points: int, quantity: int):
        super().__init__(name="Potions", health_points=health_points, quantity=quantity)


class Player(BaseModel):
    max_health_points: int
    health_points: int
    is_fighting: bool
    gold_coins: int
    potions: Potions


class Warrior(Player):
    type: Literal["warrior"] = "warrior"
    sword: Sword
    shield: Shield


class Mage(Player):
    type: Literal["mage"] = "mage"
    staff: Staff
    fire_bolt_spell: FireBoltSpell
    healing_spell: HealingSpell


class GameState(BaseModel):
    player: Union[Warrior, Mage] = Field("The Player", discriminator="type")
    command: str
    action: Action = Field(default_factory=Action)
    narration: str = ""
    current_room: DungeonRoom


# isinstance(player, Warrior)

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Potion(BaseModel):
    type: Literal["potion"] = "potion"


class Sword(BaseModel):
    type: Literal["sword"] = "sword"
    name: str
    additional_damage_points: int


class Shield(BaseModel):
    type: Literal["shield"] = "shield"
    name: str
    defensive_health_points: int
    # TODO: support condition (good, damaged, broken)


class Staff(BaseModel):
    type: Literal["staff"] = "staff"
    name: str


POTION = Potion()

BRONZE_SWORD = Sword(name="bronze sword", additional_damage_points=0)
STEEL_SWORD = Sword(name="steel sword", additional_damage_points=2)

BRONZE_SHIELD = Shield(name="bronze shield", defensive_health_points=2)
STEEL_SHIELD = Shield(name="steel shield", defensive_health_points=4)

STAFF = Staff(name="staff")
ELDER_STAFF = Staff(name="elder staff")

InventoryItem = Annotated[Potion | Sword | Shield | Staff, Field(discriminator="type")]

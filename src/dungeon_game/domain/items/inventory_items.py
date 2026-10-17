from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Potion(BaseModel):
    type: Literal["potion"] = "potion"


class Sword(BaseModel):
    type: Literal["sword"] = "sword"
    name: str
    additional_damage_points: int


ShieldCondition = Literal["good", "damaged", "broken"]


class Shield(BaseModel):
    """A shield blocks damage until it wears out. Every point of damage it
    absorbs costs a point of durability. It cannot be repaired.

    Good (more than half durability left) blocks fully, damaged (some left) blocks
    half, and broken (none left) blocks nothing."""

    type: Literal["shield"] = "shield"
    name: str
    defensive_health_points: int = Field(gt=1)
    max_durability: int
    durability: int

    @property
    def condition(self) -> ShieldCondition:
        if self.durability <= 0:
            return "broken"
        if self.durability * 2 > self.max_durability:
            return "good"
        return "damaged"

    @property
    def state(self) -> str:
        """The condition as it should appear in narration."""
        if self.condition == "good":
            return "in good condition"
        if self.condition == "damaged":
            return "damaged"
        return "broken and useless"

    @property
    def block_points(self) -> int:
        """The damage this shield absorbs from a blow in its current condition."""
        if self.condition == "good":
            return self.defensive_health_points
        if self.condition == "damaged":
            return max(1, self.defensive_health_points // 2)
        return 0

    def with_worn(self, absorbed: int) -> "Shield":
        """Return a copy that lost one durability point per damage point absorbed."""
        return self.model_copy(
            update={"durability": max(0, self.durability - absorbed)}
        )


class Staff(BaseModel):
    type: Literal["staff"] = "staff"
    name: str


POTION = Potion()

BRONZE_SWORD = Sword(name="bronze sword", additional_damage_points=0)
STEEL_SWORD = Sword(name="steel sword", additional_damage_points=2)

BRONZE_SHIELD = Shield(
    name="bronze shield", defensive_health_points=2, max_durability=6, durability=6
)
STEEL_SHIELD = Shield(
    name="steel shield", defensive_health_points=4, max_durability=10, durability=10
)

STAFF = Staff(name="staff")
ELDER_STAFF = Staff(name="elder staff")

InventoryItem = Annotated[Potion | Sword | Shield | Staff, Field(discriminator="type")]

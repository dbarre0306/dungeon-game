from __future__ import annotations

from typing import Literal

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


class OffensiveWeapon(BaseModel):
    name: str
    bonus_points: int


class DefensiveWeapon(BaseModel):
    name: str
    health_points: int
    condition: WeaponCondition


class HealingPower(BaseModel):
    name: str
    health_points: int
    quantity: int


class Player(BaseModel):
    player_type: Literal["warrior", "mage"]
    max_health_points: int
    health_points: int
    is_fighting: bool
    offensive_weapon: OffensiveWeapon
    defensive_weapon: DefensiveWeapon | None
    healing_powers: list[HealingPower]  # cannot exceed max health points when used
    gold_coins: int


class GameState(BaseModel):
    player: Player
    command: str
    action: Action = Field(default_factory=Action)
    narration: str = ""
    current_room: DungeonRoom

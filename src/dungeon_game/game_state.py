from __future__ import annotations
from typing import Literal, TypedDict

ActionType = Literal[
    "explore", "combat", "shop", "drink_potion", "open_chest", "multiple", "unknown"
]
ExploreOption = Literal["left", "right", "forward", "backward", "look"]

WeaponCondition = Literal["good", "cracked", "broken"]


class Action(TypedDict):
    action: ActionType | None
    explore_option: ExploreOption | None


class DungeonRoom(TypedDict):
    id: str
    initial_facts: list[str]
    events: list[str]
    next_room: DungeonRoom | None


class OffensiveWeapon(TypedDict):
    name: str
    bonus_points: int


class DefensiveWeapon(TypedDict):
    name: str
    health_points: int
    condition: WeaponCondition


class HealingPower(TypedDict):
    name: str
    health_points: int
    quantity: int


class Player(TypedDict):
    player_type: Literal["warrior", "mage"]
    max_health_points: int
    health_points: int
    is_fighting: bool
    offensive_weapon: OffensiveWeapon
    defensive_weapon: DefensiveWeapon | None
    healing_powers: list[HealingPower]  # cannot exceed max health points when used
    gold_coins: int


class GameState(TypedDict):
    player: Player
    command: str
    action: Action
    narration: str
    current_room: DungeonRoom

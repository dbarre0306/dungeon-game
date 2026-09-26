from __future__ import annotations
from typing import Literal, TypedDict

ActionType = Literal[
    "explore", "combat", "shop", "drink_potion", "open_chest", "multiple", "unknown"
]
ExploreOption = Literal["left", "right", "forward", "backward", "look"]


class Action(TypedDict):
    action: ActionType | None
    explore_option: ExploreOption | None


class DungeonRoom(TypedDict):
    id: str
    initial_facts: list[str]
    events: list[str]
    next_room: DungeonRoom | None


class PlayerState(TypedDict):
    player_type: Literal["warrior", "mage"]
    health_points: int


class GameState(TypedDict):
    player: PlayerState
    command: str
    action: Action
    narration: str
    current_room: DungeonRoom

from typing import Literal

from pydantic import BaseModel

ActionType = Literal[
    "explore",
    "look",
    "attack",
    "shop",
    "drink_potion",
    "open_chest",
    "multiple",
    "unknown",
]
ExploreDirection = Literal["left", "right", "forward", "backward"]


class Intent(BaseModel):
    type: ActionType | None = None
    explore_direction: ExploreDirection | None = None

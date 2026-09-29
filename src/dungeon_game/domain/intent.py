from typing import Literal

from pydantic import BaseModel

ActionType = Literal[
    "explore", "attack", "shop", "drink_potion", "open_chest", "multiple", "unknown"
]
ExploreDirection = Literal["left", "right", "forward", "backward", "look"]


class Intent(BaseModel):
    type: ActionType | None = None
    explore_direction: ExploreDirection | None = None

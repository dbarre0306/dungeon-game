from typing import Literal

from pydantic import BaseModel

ActionType = Literal[
    "explore", "attack", "shop", "drink_potion", "open_chest", "multiple", "unknown"
]
ExploreOption = Literal["left", "right", "forward", "backward", "look"]


class Intent(BaseModel):
    type: ActionType | None = None
    explore_option: ExploreOption | None = None

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

    def is_explore(self) -> bool:
        return self.type == "explore"

    def is_explore_forward(self) -> bool:
        return self.type == "explore" and self.explore_direction == "forward"

    def is_explore_left(self) -> bool:
        return self.type == "explore" and self.explore_direction == "left"

    def is_explore_right(self) -> bool:
        return self.type == "explore" and self.explore_direction == "right"

    def is_look(self) -> bool:
        return self.type == "look"

    def is_attack(self) -> bool:
        return self.type == "attack"

    def is_shop(self) -> bool:
        return self.type == "shop"

    def is_drink_potion(self) -> bool:
        return self.type == "drink_potion"

    def is_open_chest(self) -> bool:
        return self.type == "open_chest"

    def is_multiple(self) -> bool:
        return self.type == "multiple"

    def is_unknown(self) -> bool:
        return self.type == "unknown"

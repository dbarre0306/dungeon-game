from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, Field

from dungeon_game.domain.intent import Intent

if TYPE_CHECKING:
    from dungeon_game.game_state import GameState


# Base class for all dungeon rooms
class DungeonRoom(BaseModel, ABC):
    history: Annotated[list[str], operator.add] = Field(default_factory=list)

    @abstractmethod
    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        """This is an abstract method. Subclasses must implement it."""
        ...

    @abstractmethod
    def get_room_facts(self, state: GameState) -> list[str]:
        """This is an abstract method. Subclasses must implement it."""
        ...

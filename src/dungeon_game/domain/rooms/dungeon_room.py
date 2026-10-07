import operator
from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, Field

from dungeon_game.domain.intent import Intent


# Base class for all dungeon rooms
class DungeonRoom(BaseModel, ABC):
    history: Annotated[list[str], operator.add] = Field(default_factory=list)

    @abstractmethod
    def is_valid_action(self, action: Intent) -> tuple[bool, str | None]:
        """This is an abstract method. Subclasses must implement it."""
        ...

    @abstractmethod
    def get_room_facts(self) -> list[str]:
        """This is an abstract method. Subclasses must implement it."""
        ...

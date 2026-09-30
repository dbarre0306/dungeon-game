import operator
from abc import abstractmethod
from typing import Annotated

from pydantic import BaseModel

from dungeon_game.domain.intent import Intent


# Base class for all dungeon rooms
class DungeonRoom(BaseModel):
    events: Annotated[list[str], operator.add] = []
    room_description: str | None = None

    @abstractmethod
    def is_valid_action(self, action: Intent) -> tuple[bool, str | None]:
        """This is an abstract method. Subclasses must implement it."""
        pass

    @abstractmethod
    def get_initial_facts(self) -> list[str]:
        """This is an abstract method. Subclasses must implement it."""
        pass

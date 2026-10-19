import operator
from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, Field

from dungeon_game.domain.intent import Intent


# Base class for all dungeon rooms
class DungeonRoom(BaseModel, ABC):
    history: Annotated[list[str], operator.add] = Field(default_factory=list)

    def is_valid_intent(self, intent: Intent) -> tuple[bool, str | None]:
        """Drinking a potion and casting a healing spell work in every room;
        any other intent is up to the room."""
        if intent.is_drink_potion() or intent.is_cast_healing():
            return (True, None)
        return self._is_valid_room_intent(intent)

    @abstractmethod
    def _is_valid_room_intent(self, intent: Intent) -> tuple[bool, str | None]:
        """This is an abstract method. Subclasses must implement it."""
        ...

    @abstractmethod
    def get_room_facts(self) -> list[str]:
        """This is an abstract method. Subclasses must implement it."""
        ...

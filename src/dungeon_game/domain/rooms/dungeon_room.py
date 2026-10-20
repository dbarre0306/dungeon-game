import operator
from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, Field

from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.intent import Intent, IntentType

# Intents that are legal in every room.
_ANY_ROOM_INTENTS: frozenset[IntentType] = frozenset(
    {"look", "drink_potion", "cast_healing"}
)


# Base class for all dungeon rooms
class DungeonRoom(BaseModel, ABC):
    history: Annotated[list[str], operator.add] = Field(default_factory=list)

    def get_legal_intents(self, player: Player) -> frozenset[IntentType]:
        """The intents this room allows the given player to attempt: the ones
        legal in every room plus the room's own, limited to what the player's
        class can do. `multiple` and `unknown` are never listed."""
        legal = _ANY_ROOM_INTENTS | self._legal_room_intents()
        return legal & frozenset(player.get_supported_intents())

    @abstractmethod
    def _legal_room_intents(self) -> frozenset[IntentType]:
        """This is an abstract method. Subclasses must implement it."""
        ...

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

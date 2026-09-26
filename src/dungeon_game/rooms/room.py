from abc import abstractmethod

from dungeon_game.game_state import Action, DungeonRoom


class Room:

    def __init__(self, room: DungeonRoom):
        self._room = room

    @abstractmethod
    def is_valid_action(self, action: Action) -> tuple[bool, str | None]:
        """This is an abstract method. Subclasses must implement it."""
        pass

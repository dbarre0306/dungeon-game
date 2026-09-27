from dungeon_game.game_state import Action, DungeonRoom
from dungeon_game.rooms.room import Room


class CaveEntrance(Room):

    def __init__(self, room: DungeonRoom):
        super().__init__(room)

    def is_valid_action(self, action: Action) -> tuple[bool, str | None]:
        if action.explore_option == "look":
            return (True, None)
        if action.explore_option == "forward":
            return (True, None)
        return False, "You cannot run away.  You must enter the cave."

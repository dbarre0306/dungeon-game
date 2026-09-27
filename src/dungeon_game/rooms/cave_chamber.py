from dungeon_game.game_state import Action, DungeonRoom
from dungeon_game.rooms.room import Room


class CaveChamber(Room):

    def __init__(self, room: DungeonRoom):
        super().__init__(room)

    def is_valid_action(self, action: Action) -> tuple[bool, str | None]:
        if action.explore_option == "look":
            return (True, None)
        elif action.explore_option == "left":
            return (True, None)
        elif action.explore_option == "right":
            return (True, None)
        return False, "You must go either left or right."

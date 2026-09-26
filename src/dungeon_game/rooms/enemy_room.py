from dungeon_game.game_state import Action, DungeonRoom
from dungeon_game.rooms.room import Room


class EnemyRoom(Room):

    def __init__(self, room: DungeonRoom):
        super().__init__(room)

    def is_valid_action(self, action: Action) -> tuple[bool, str | None]:
        return (True, None)

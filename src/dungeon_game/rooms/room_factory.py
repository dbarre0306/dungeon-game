from re import I

from dungeon_game.game_state import DungeonRoom
from dungeon_game.rooms.cave_chamber import CaveChamber
from dungeon_game.rooms.cave_entrance import CaveEntrance
from dungeon_game.rooms.enemy_room import EnemyRoom
from dungeon_game.rooms.room import Room


def create_room(room: DungeonRoom) -> Room | None:
    match room.id:
        case "cave_entrance":
            return CaveEntrance(room)
        case "cave_chamber":
            return CaveChamber(room)
        case "enemy_room":
            return EnemyRoom(room)
    return None

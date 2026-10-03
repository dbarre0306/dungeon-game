from dungeon_game.domain.npc.enemy import Enemy
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


# Base class for all dungeon rooms that contain an enemy to fight
class CombatRoom(DungeonRoom):
    enemy: Enemy

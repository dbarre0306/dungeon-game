from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom

NONEXISTENT_WEAPON_REFUSAL = (
    "Tell the player that they do not have the weapon they named, so no attack "
    "happens. Using the player facts, say what they do carry instead and suggest "
    "they use it. Do NOT describe them swinging, casting or striking, and do NOT "
    "imply they once owned the weapon. Do NOT describe any damage."
)


# Base class for all dungeon rooms that contain an enemy to fight
class CombatRoom(DungeonRoom):
    enemy: Enemy

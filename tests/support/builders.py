"""Builders for the exact dungeons and players a scenario needs, so tests never
depend on what `DungeonFactory` happens to randomize."""

from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.rooms.cave_chamber import CaveChamber
from dungeon_game.domain.rooms.cave_entrance import CaveEntrance
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.domain.rooms.shop_room import ShopRoom
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.domain.rooms.trap_room import TrapRoom
from dungeon_game.domain.rooms.treasure_room import TreasureRoom
from dungeon_game.game_state import GameState


def goblin(health_points: int = 10) -> Enemy:
    return Enemy(
        name="goblin",
        weapon="dagger",
        max_health_points=10,
        health_points=health_points,
        hit_bonus=0,
    )


def monster_dungeon(enemy: Enemy | None = None) -> Dungeon:
    """Entrance, chamber, then a monster room, as the game currently lays out."""
    return Dungeon(
        rooms=[
            CaveEntrance(),
            CaveChamber(),
            MonsterRoom(enemy=enemy or goblin()),
            ShopRoom(),
            ThroneRoom(),
        ]
    )


def trap_dungeon(trap_type: str = "poison dart") -> Dungeon:
    """Entrance, chamber, then a trap room."""
    return Dungeon(
        rooms=[
            CaveEntrance(),
            CaveChamber(),
            TrapRoom(trap_type=trap_type),
            ShopRoom(),
            ThroneRoom(),
        ]
    )


def serpent(health_points: int = 15) -> Enemy:
    return Enemy(
        name="serpent",
        weapon="fangs",
        max_health_points=15,
        health_points=health_points,
        hit_bonus=0,
    )


def treasure_dungeon(
    serpent_side: str = "right", serpent_health_points: int = 15
) -> Dungeon:
    """Entrance, chamber, then a treasure room with the serpent in the given chest."""
    return Dungeon(
        rooms=[
            CaveEntrance(),
            CaveChamber(),
            TreasureRoom(
                serpent_side=serpent_side,
                enemy=serpent(health_points=serpent_health_points),
            ),
            ShopRoom(),
            ThroneRoom(),
        ]
    )


def new_game_state(player, dungeon: Dungeon, command: str = "look") -> GameState:
    return GameState(player=player, dungeon=dungeon, command=command)

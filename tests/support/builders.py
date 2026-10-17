"""Builders for the exact dungeons and players a scenario needs, so tests never
depend on what `DungeonFactory` happens to randomize."""

from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.rooms.cave_chamber import CaveChamber
from dungeon_game.domain.rooms.cave_entrance import CaveEntrance
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.domain.rooms.shop_room import ShopRoom
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.domain.rooms.trap_room import TrapRoom
from dungeon_game.domain.rooms.treasure_room import TreasureRoom
from dungeon_game.game_state import GameState


def _warrior_merchant() -> Merchant:
    return Merchant(merchandise=create_default_warrior().get_supported_merchandise())


def goblin(health_points: int = 10) -> Enemy:
    return Enemy(
        name="goblin",
        weapon="dagger",
        max_health_points=10,
        health_points=health_points,
        hit_bonus=0,
    )


def full_dungeon() -> Dungeon:
    """Entrance, chamber, monster room, shop and throne room, as the game
    currently lays out."""
    return Dungeon(
        rooms=[
            CaveEntrance(),
            CaveChamber(),
            MonsterRoom(enemy=goblin()),
            ShopRoom(merchant=_warrior_merchant()),
            ThroneRoom(),
        ]
    )


def monster_dungeon(enemy: Enemy | None = None) -> Dungeon:
    """A monster room, then a chamber."""
    return Dungeon(rooms=[MonsterRoom(enemy=enemy or goblin()), CaveChamber()])


def trap_dungeon(trap_type: str = "poison dart") -> Dungeon:
    """A trap room, then a chamber."""
    return Dungeon(rooms=[TrapRoom(trap_type=trap_type), CaveChamber()])


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
    """A treasure room with the serpent in the given chest, then a chamber."""
    return Dungeon(
        rooms=[
            TreasureRoom(
                serpent_side=serpent_side,
                enemy=serpent(health_points=serpent_health_points),
            ),
            CaveChamber(),
        ]
    )


def shop_dungeon() -> Dungeon:
    """A shop room, then a chamber."""
    return Dungeon(
        rooms=[
            ShopRoom(merchant=_warrior_merchant()),
            CaveChamber(),
        ]
    )


def new_game_state(player, dungeon: Dungeon, command: str = "look") -> GameState:
    return GameState(
        player=player,
        dungeon=dungeon,
        command=command,
    )

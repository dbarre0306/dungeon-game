import random

from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.rooms.cave_chamber import CaveChamber
from dungeon_game.domain.rooms.cave_entrance import CaveEntrance
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.domain.rooms.shop_room import ShopRoom
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.domain.rooms.trap_room import TrapRoom
from dungeon_game.domain.rooms.treasure_room import TreasureRoom


class DungeonFactory:
    def generate(self, merchant: Merchant) -> Dungeon:
        remaining_rooms = ["treasure", "monster", "trap"]
        first_room, remaining_rooms = self._pick_first_combat_room(remaining_rooms)
        second_room = random.choice(remaining_rooms)

        return Dungeon(
            rooms=[
                CaveEntrance(),
                CaveChamber(),
                self._generate_combat_room(first_room),
                self._generate_combat_room(second_room),
                ShopRoom(merchant=merchant),
                self._generate_throne_room(),
            ]
        )

    @staticmethod
    def _generate_throne_room() -> ThroneRoom:
        return ThroneRoom(
            enemy=Enemy(
                name="troll",
                weapon="large spiked wooden club",
                max_health_points=30,
                health_points=30,
                hit_bonus=4,
                damage_die_sides=8,
                damage_bonus=2,
            )
        )

    @staticmethod
    def _pick_first_combat_room(rooms: list[str]) -> tuple[str, list[str]]:
        room = random.choice(rooms)
        return room, DungeonFactory._other_rooms(rooms, room)

    @staticmethod
    def _other_rooms(rooms: list[str], room: str) -> list[str]:
        return [r for r in rooms if r != room]

    @staticmethod
    def _generate_combat_room(room: str) -> DungeonRoom:
        match room:
            case "treasure":
                return TreasureRoom(
                    serpent_side=random.choice(["left", "right"]),
                    enemy=Enemy(
                        name="serpent",
                        weapon="fangs",
                        max_health_points=12,
                        health_points=12,
                        hit_bonus=3,
                        damage_die_sides=6,
                    ),
                )
            case "monster":
                monster_name = random.choice(["goblin", "orc", "giant rat"])
                return MonsterRoom(enemy=DungeonFactory._create_monster(monster_name))
            case "trap":
                trap_type = random.choice(["poison dart", "swinging blade"])
                return TrapRoom(trap_type=trap_type)

    @staticmethod
    def _create_monster(monster: str) -> Enemy:
        match monster:
            case "goblin":
                return Enemy(
                    name="goblin",
                    weapon="dagger",
                    max_health_points=10,
                    health_points=10,
                    hit_bonus=3,
                    damage_die_sides=4,
                    damage_bonus=1,
                )
            case "orc":
                return Enemy(
                    name="orc",
                    weapon="battle ax",
                    max_health_points=16,
                    health_points=16,
                    hit_bonus=4,
                    damage_die_sides=6,
                    damage_bonus=1,
                )
            case "giant rat":
                return Enemy(
                    name="giant rat",
                    weapon="razor sharp teeth",
                    max_health_points=7,
                    health_points=7,
                    hit_bonus=2,
                    damage_die_sides=3,
                )
            case _:
                raise ValueError(f"unknown monster: {monster!r}")

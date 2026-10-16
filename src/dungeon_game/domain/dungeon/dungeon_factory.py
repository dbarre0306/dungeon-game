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
                ShopRoom(merchant=merchant),
                self._generate_combat_room(first_room),
                self._generate_combat_room(second_room),
                ThroneRoom(),
            ]
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
                        max_health_points=15,
                        health_points=15,
                        hit_bonus=0,
                    ),
                )
            case "monster":
                monster_name = random.choice(["goblin", "orc", "giant rat"])
                return MonsterRoom(
                    enemy=Enemy(
                        name=monster_name,
                        weapon=DungeonFactory._get_monster_weapon(monster_name),
                        max_health_points=10,
                        health_points=10,
                        hit_bonus=0,
                    )
                )
            case "trap":
                trap_type = random.choice(["poison dart", "swinging blade"])
                return TrapRoom(trap_type=trap_type)

    @staticmethod
    def _get_monster_weapon(monster: str) -> str:
        match monster:
            case "goblin":
                return "dagger"
            case "orc":
                return "battle ax"
            case "giant rat":
                return "razor sharp teeth"

import random

from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.npc.enemy import Enemy
from dungeon_game.domain.rooms.cave_chamber import CaveChamber
from dungeon_game.domain.rooms.cave_entrance import CaveEntrance
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.domain.rooms.enemy_room import EnemyRoom
from dungeon_game.domain.rooms.shop_room import ShopRoom
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.domain.rooms.trap_room import TrapRoom
from dungeon_game.domain.rooms.treasure_room import TreasureRoom


class DungeonFactory:
    def generate(self) -> Dungeon:
        remaining_rooms = ["treasure", "enemy", "trap"]
        first_room, remaining_rooms = self._pick_first_challenge_room(remaining_rooms)
        second_room = random.choice(remaining_rooms)

        return Dungeon(
            rooms=[
                CaveEntrance(),
                CaveChamber(),
                self._generate_challenge_room(first_room),
                self._generate_challenge_room(second_room),
                ShopRoom(),
                ThroneRoom(),
            ]
        )

    @staticmethod
    def _pick_first_challenge_room(rooms: list[str]) -> tuple[str, list[str]]:
        # TODO: change this back; it's temporary
        # room = random.choice(rooms)
        room = "enemy"
        return room, DungeonFactory._other_rooms(rooms, room)

    @staticmethod
    def _other_rooms(rooms: list[str], room: str) -> list[str]:
        return [r for r in rooms if r != room]

    @staticmethod
    def _generate_challenge_room(room: str) -> DungeonRoom:
        match room:
            case "treasure":
                return TreasureRoom()
            case "enemy":
                enemy_name = random.choice(["goblin", "orc", "rat"])
                return EnemyRoom(
                    enemy=Enemy(
                        name=enemy_name,
                        description=DungeonFactory._get_enemy_description(enemy_name),
                        health_points=10,
                    )
                )
            case "trap":
                return TrapRoom()

    @staticmethod
    def _get_enemy_description(enemy: str) -> str:
        match enemy:
            case "goblin":
                return "goblin with a dagger"
            case "orc":
                return "orc with a battle ax"
            case "rat":
                return "giant rat with razor sharp teeth"

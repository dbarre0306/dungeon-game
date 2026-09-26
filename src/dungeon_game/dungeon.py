from __future__ import annotations

import random
from typing import Literal, TypedDict


class DungeonRoom(TypedDict):
    id: str
    facts: list[str]
    next_room: DungeonRoom | None


class DungeonFactory:

    def generate(self) -> DungeonRoom:
        return self._generate_cave_entrance()

    def _generate_cave_entrance(self) -> DungeonRoom:
        return {
            "id": "cave_entrance",
            "facts": ["The player is standing at the entrance of the cave."],
            "next_room": self._generate_chamber(),
        }

    def _generate_chamber(self) -> DungeonRoom:
        challenge_room = self._generate_first_challenge_room(
            ["treasure", "enemy", "trap"]
        )
        return {
            "id": "cave_chamber",
            "facts": [
                "The player is in the cave chamber.",
                "The chamber has a passageway to the left and another the right."
                "There is a flicking torch on the wall.",
                "There may be silence or noises coming from either passageway.",
            ],
            "next_room": challenge_room,
        }

    def _generate_first_challenge_room(self, rooms: list[str]) -> DungeonRoom:
        room = random.choice(rooms)
        other_rooms = self._remove_room(rooms, room)
        match room:
            case "treasure":
                return self._generate_treasure_room(
                    self._generate_second_challenge_room(other_rooms)
                )
            case "enemy":
                return self._generate_enemy_room(
                    self._generate_second_challenge_room(other_rooms)
                )
            case "trap":
                return self._generate_trap_room(
                    self._generate_second_challenge_room(other_rooms)
                )

    @staticmethod
    def _remove_room(rooms: list[str], room_to_remove: str) -> list[str]:
        return [room for room in rooms if room != room_to_remove]

    def _generate_second_challenge_room(self, rooms: list[str]):
        room = random.choice(rooms)
        match room:
            case "treasure":
                return self._generate_treasure_room(self._generate_shop_room())
            case "enemy":
                return self._generate_enemy_room(self._generate_shop_room())
            case "trap":
                return self._generate_trap_room(self._generate_shop_room())

    @staticmethod
    def _generate_treasure_room(next_room: DungeonRoom) -> DungeonRoom:
        return {
            "id": "treasure_room",
            "facts": [
                "There are two identical chests to the left and right.",
                "One chest contains gold coins.",
                "The other chest contains a serpent.",
                "There is only one passageway out of this room.",
            ],
            "next_room": next_room,
        }

    @staticmethod
    def _generate_enemy_room(next_room: DungeonRoom) -> DungeonRoom:
        enemy = random.choice(["goblin", "orc with a battle ax", "giant rat"])
        return {
            "id": "enemy_room",
            "facts": [f"An {enemy} is in this room."],
            "next_room": next_room,
        }

    @staticmethod
    def _generate_trap_room(next_room: DungeonRoom) -> DungeonRoom:
        return {
            "id": "trap_room",
            "facts": [
                "There are gold coins on the other side of the room.",
                "There is only one passageway forward.",
            ],
            "next_room": next_room,
        }

    def _generate_shop_room(self) -> DungeonRoom:
        return {
            "id": "shop_room",
            "facts": [
                "There is a merchant selling stuff.",
                "There is only one passageway forward.",
            ],
            "next_room": self._generate_throne_room(),
        }

    @staticmethod
    def _generate_throne_room() -> DungeonRoom:
        return {
            "id": "throne_room",
            "facts": [
                "There is a troll twice the player's size sitting on a stone throne.",
                "The troll has a large spiked wooden club.",
                "The troll has the Amulet of Valdorin around his neck.",
            ],
            "next_room": None,
        }

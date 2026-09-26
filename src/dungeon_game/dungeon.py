from __future__ import annotations

import random
from typing import TypedDict


class DungeonRoom(TypedDict):
    id: str
    facts: list[str]
    next_room: DungeonRoom | None


def generate_dungeon() -> DungeonRoom:
    return generate_cave_entrance()


def generate_cave_entrance() -> DungeonRoom:
    return {
        "id": "cave_entrance",
        "facts": ["The player is standing at the entrance of the cave."],
        "next_room": generate_chamber(),
    }


def generate_chamber() -> DungeonRoom:
    challenge_room = generate_first_challenge_room(["treasure", "enemy", "trap"])
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


def generate_first_challenge_room(rooms: list[str]) -> DungeonRoom:
    room = random.choice(rooms)
    other_rooms = remove_room(rooms, room)
    match room:
        case "treasure":
            return generate_treasure_room(generate_second_challenge_room(other_rooms))
        case "enemy":
            return generate_enemy_room(generate_second_challenge_room(other_rooms))
        case "trap":
            return generate_trap_room(generate_second_challenge_room(other_rooms))


def remove_room(rooms: list[str], room_to_remove: str) -> list[str]:
    return [room for room in rooms if room != room_to_remove]


def generate_second_challenge_room(rooms: list[str]):
    room = random.choice(rooms)
    match room:
        case "treasure":
            return generate_treasure_room(generate_shop_room())
        case "enemy":
            return generate_enemy_room(generate_shop_room())
        case "trap":
            return generate_trap_room(generate_shop_room())


def generate_treasure_room(next_room: DungeonRoom) -> DungeonRoom:
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


def generate_enemy_room(next_room: DungeonRoom) -> DungeonRoom:
    return {
        "id": "enemy_room",
        "facts": ["An enemy is in this room"],
        "next_room": next_room,
    }


def generate_trap_room(next_room: DungeonRoom) -> DungeonRoom:
    return {
        "id": "trap_room",
        "facts": [
            "There are gold coins on the other side of the room.",
            "There is only one passageway forward.",
        ],
        "next_room": next_room,
    }


def generate_shop_room() -> DungeonRoom:
    return {
        "id": "shop_room",
        "facts": [
            "There is a merchant selling stuff.",
            "There is only one passageway forward.",
        ],
        "next_room": generate_throne_room(),
    }


def generate_throne_room() -> DungeonRoom:
    return {
        "id": "throne_room",
        "facts": [
            "There is a troll twice the player's size sitting on a stone throne.",
            "The troll has a large spiked wooden club.",
            "The troll has the Amulet of Valdorin around his neck.",
        ],
        "next_room": None,
    }

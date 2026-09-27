import random

from dungeon_game.game_state import DungeonRoom


class DungeonFactory:

    def generate(self) -> DungeonRoom:
        return self._generate_cave_entrance()

    def _generate_cave_entrance(self) -> DungeonRoom:
        return DungeonRoom(
            id="cave_entrance",
            initial_facts=["The player is standing at the entrance of the cave."],
            events=[],
            next_room=self._generate_chamber(),
        )

    def _generate_chamber(self) -> DungeonRoom:
        challenge_room = self._generate_first_challenge_room(
            ["treasure", "enemy", "trap"]
        )
        return DungeonRoom(
            id="cave_chamber",
            initial_facts=[
                "The player is in the cave chamber.",
                "The chamber has a passageway to the left and another the right."
                "There is a flicking torch on the wall.",
                "There may be silence or noises coming from either passageway.",
            ],
            events=[],
            next_room=challenge_room,
        )

    def _generate_first_challenge_room(self, rooms: list[str]) -> DungeonRoom:
        # TODO: change this back; it's temporary
        # room = random.choice(rooms)
        room = "enemy"
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
        return DungeonRoom(
            id="treasure_room",
            initial_facts=[
                "There are two identical chests to the left and right.",
                "One chest contains gold coins.",
                "The other chest contains a serpent.",
                "There is only one passageway out of this room.",
            ],
            events=[],
            next_room=next_room,
        )

    @staticmethod
    def _generate_enemy_room(next_room: DungeonRoom) -> DungeonRoom:
        enemy = random.choice(["goblin", "orc with a battle ax", "giant rat"])
        return DungeonRoom(
            id="enemy_room",
            initial_facts=[f"An {enemy} is in this room."],
            events=[],
            next_room=next_room,
        )

    @staticmethod
    def _generate_trap_room(next_room: DungeonRoom) -> DungeonRoom:
        return DungeonRoom(
            id="trap_room",
            initial_facts=[
                "There are gold coins on the other side of the room.",
                "There is only one passageway forward.",
            ],
            events=[],
            next_room=next_room,
        )

    def _generate_shop_room(self) -> DungeonRoom:
        return DungeonRoom(
            id="shop_room",
            initial_facts=[
                "There is a merchant selling stuff.",
                "There is only one passageway forward.",
            ],
            events=[],
            next_room=self._generate_throne_room(),
        )

    @staticmethod
    def _generate_throne_room() -> DungeonRoom:
        return DungeonRoom(
            id="throne_room",
            initial_facts=[
                "There is a troll twice the player's size sitting on a stone throne.",
                "The troll has a large spiked wooden club.",
                "The troll has the Amulet of Valdorin around his neck.",
            ],
            events=[],
            next_room=None,
        )

from typing import Annotated, Any

from pydantic import BaseModel, Field

from dungeon_game.domain.rooms.cave_chamber import CaveChamber
from dungeon_game.domain.rooms.cave_entrance import CaveEntrance
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.domain.rooms.shop_room import ShopRoom
from dungeon_game.domain.rooms.throne_room import ThroneRoom
from dungeon_game.domain.rooms.trap_room import TrapRoom
from dungeon_game.domain.rooms.treasure_room import TreasureRoom

Room = Annotated[
    CaveEntrance | CaveChamber | MonsterRoom | TreasureRoom | TrapRoom | ShopRoom | ThroneRoom,
    Field(discriminator="type"),
]


class Dungeon(BaseModel):
    """An ordered sequence of rooms; a room's position in the list is its identity."""

    rooms: list[Room]

    def get_room(self, index: int) -> DungeonRoom:
        return self.rooms[index]

    def get_next_room(self, index: int) -> DungeonRoom | None:
        next_index = index + 1
        if next_index >= len(self.rooms):
            return None
        return self.rooms[next_index]

    def with_room_updated(self, index: int, **updates: Any) -> "Dungeon":
        """Return a new Dungeon with the room at `index` replaced by a copy
        of that room with `updates` applied.

        A field whose type is `Annotated[T, reducer]` is merged via
        `reducer(current, update)` instead of being overwritten, mirroring
        LangGraph's reducer semantics for plain (non-graph-state) models.
        """
        room = self.rooms[index]
        for field_name, field_info in type(room).model_fields.items():
            if field_name not in updates:
                continue
            for reducer in field_info.metadata:
                if callable(reducer):
                    updates[field_name] = reducer(getattr(room, field_name), updates[field_name])
                    break
        updated_room = room.model_copy(update=updates)
        new_rooms = list(self.rooms)
        new_rooms[index] = updated_room
        return self.model_copy(update={"rooms": new_rooms})

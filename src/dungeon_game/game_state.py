from pydantic import BaseModel, Field

from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.intent import Intent
from dungeon_game.domain.player.mage import Mage
from dungeon_game.domain.player.warrior import Warrior
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class GameState(BaseModel):
    player: Warrior | Mage = Field(discriminator="type")
    dungeon: Dungeon
    command: str
    intent: Intent = Field(default_factory=Intent)
    narration: str = ""

    def get_current_room(self) -> DungeonRoom:
        return self.dungeon.get_room(self.player.current_room_index)

    def get_next_room(self) -> DungeonRoom | None:
        return self.dungeon.get_next_room(self.player.current_room_index)


# TODO: include entire conversation history to redisplay if save game for later
# isinstance(player, Warrior)

from pydantic import BaseModel, Field

from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.intent import Intent
from dungeon_game.domain.player.mage import Mage
from dungeon_game.domain.player.warrior import Warrior


class GameState(BaseModel):
    player: Warrior | Mage = Field(discriminator="type")
    dungeon: Dungeon
    command: str
    action: Intent = Field(default_factory=Intent)
    narration: str = ""


# TODO: include entire conversation history to redisplay if save game for later
# isinstance(player, Warrior)

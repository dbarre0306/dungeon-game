from pydantic import BaseModel, Field

from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.misc.action import Action
from dungeon_game.domain.player.mage import Mage
from dungeon_game.domain.player.warrior import Warrior


class GameState(BaseModel):
    player: Warrior | Mage = Field(discriminator="type")
    dungeon: Dungeon
    command: str
    action: Action = Field(default_factory=Action)
    narration: str = ""


# TODO: include entire conversation history to redisplay if save game for later
# isinstance(player, Warrior)

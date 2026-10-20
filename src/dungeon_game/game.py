import os

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.actors.player.mage import create_default_mage
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from dungeon_game.game_graph import GameGraph


class Game:
    def __init__(self):
        # self.player = create_default_warrior()
        self.player = create_default_mage()
        merchant = Merchant(merchandise=self.player.get_supported_merchandise())

        dungeon_factory = DungeonFactory()
        self.dungeon = dungeon_factory.generate(merchant)

        model_name = os.getenv("MODEL", "gpt-4o-mini")
        # A bare name defaults to OpenAI; "provider:name" is used as given.
        model = model_name if ":" in model_name else f"openai:{model_name}"
        router_agent = RouterAgent(model)
        dungeon_master_agent = DungeonMasterAgent(model)

        self.game_graph = GameGraph(router_agent, dungeon_master_agent)

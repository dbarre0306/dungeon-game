from langchain.agents import create_agent
from pydantic import BaseModel


class DungeonMasterResponse(BaseModel):
    narration: str


def create_dungeon_master_agent(model: str):
    return create_agent(
        model=model,
        system_prompt="You are the Dungeon Master for this game. "
        "The game is similar to Dungeons and Dragons.  As the Dungeon Master "
        "you control the flow of the game through narration.  You have a way "
        "with words in that you can make it fun and scary at the same time. "
        "In this game, the player must retrieve the Amulet of Valdorin that was "
        "was stolen by a troll who lives in the Dungeon of Mistwood.",
        response_format=DungeonMasterResponse,
    )

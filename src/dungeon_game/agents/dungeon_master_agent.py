from langchain.agents import create_agent
from pydantic import BaseModel


class DungeonMasterResponse(BaseModel):
    narration: str


class DungeonMasterAgent:
    def __init__(self, model):
        self._agent = create_agent(
            model=model,
            system_prompt="You are the Dungeon Master for this game. "
            "The game is similar to Dungeons and Dragons.  As the Dungeon Master "
            "you control the flow of the game through narration.  You have a way "
            "with words in that you can make it fun and scary at the same time. "
            "In this game, the player must retrieve the Amulet of Valdorin that was "
            "was stolen by a troll who lives in the Dungeon of Mistwood.",
            response_format=DungeonMasterResponse,
        )

    def invoke(self, msg: str) -> DungeonMasterResponse:
        user_msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "Construct a narrative which addresses the "
                    "player based on the following: \n\n"
                    f"{msg}"
                    "\n\n"
                    "The Dungeon Master Narration Rules to live by:\n"
                    "- Keep it to two or three sentences at most. \n"
                    "- Do NOT be overdramatic!!!\n"
                    "- Do NOT make up any facts.",
                }
            ]
        }

        result = self._agent.invoke(user_msg)
        return result["structured_response"]

from langchain.agents import create_agent
from pydantic import BaseModel

from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


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

    def invoke(self, room: DungeonRoom, player: Player, msg: str) -> DungeonMasterResponse:
        user_msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "The Dungeon Master Narration Rules are:\n"
                    "- Keep it to two or three sentences at most. \n"
                    "- Do NOT be overdramatic!!!\n"
                    "- Do NOT make up any facts."
                    "\n\n"
                    "Player Facts:\n"
                    f"{self._format_list([player.get_facts()])}"
                    "\n\n"
                    "Room Facts:\n"
                    f"{self._room_facts(room)}"
                    "\n\n"
                    f"{self._room_history(room)}"
                    "Construct a narrative which addresses the "
                    "player based on the following (try not to repeat previous stuff from the room's history): \n\n"
                    f"{msg}",
                }
            ]
        }

        # TODO: remove this comment when it is no longer needed
        # print(f"TO AGENT: {user_msg['messages'][0]['content']}")
        # print("-----------")

        result = self._agent.invoke(user_msg)
        return result["structured_response"]

    @staticmethod
    def _format_list(items: list[str]) -> str:
        return "\n".join(map(lambda f: f"- {f}", items))

    def _room_facts(self, room: DungeonRoom) -> str:
        return self._format_list(room.get_room_facts())

    def _room_history(self, room: DungeonRoom) -> str:
        if len(room.history) == 0:
            return ""
        return (
            "Room History: (The word `you` refers to the player):\n"
            f"{self._format_list(room.history)}"
            "\n\n"
        )

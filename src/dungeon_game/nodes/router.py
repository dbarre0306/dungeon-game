from typing import Any

from langchain.agents.structured_output import StructuredOutputError

from dungeon_game.game_state import GameState


class RouterNode:

    def __init__(self, router_agent):
        self._router_agent = router_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        content = (
            f"Player command: {state.command}\n"
            "\n"
            "Do your best to categorize the player's command to only one of the "
            "following categories: `explore`, `look`, `attack`, `shop`, `drink_potion`, or `open_chest`. "
            "If the command matches multiple categories, then categorize it as `multiple`. "
            "If there is no match, categorize it as `unknown`. "
            "\n"
            "Exploring encompasses both moving, exiting, or entering. "
            "Set explore_direction to be the player's direction which is either "
            "`left`, `right`, `forward`, or `backward`.  If the player's command doesn't specify "
            "the direction, then use `forward` by default.  If a player refers to exiting "
            "a room, they are indicating that they want to move forward through the only door."
        )
        try:
            result = self._router_agent.invoke(
                {"messages": [{"role": "user", "content": content}]}
            )
        except StructuredOutputError:
            # The model occasionally returns malformed structured output
            # (e.g. for typos or ambiguous commands). Treat it as unknown
            # rather than crashing the whole game loop.
            return {"intent": {"type": "unknown", "explore_direction": None}}
        return {
            "intent": {
                "type": result["structured_response"].action,
                "explore_direction": result["structured_response"].explore_direction,
            }
        }

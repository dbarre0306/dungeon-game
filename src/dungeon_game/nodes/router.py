from typing import Any

from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.game_state import GameState


class RouterNode:
    def __init__(self, router_agent: RouterAgent):
        self._router_agent = router_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        content = (
            f"Player command: {state.command}\n"
            "\n"
            "Do your best to categorize the player's command to only one of the "
            "following categories: `explore`, `look`, `attack`, `shop`, "
            "`drink_potion`, or `open_chest`.  If the command matches multiple "
            "categories, then categorize it as `multiple`. If there is no match, "
            "categorize it as `unknown`. "
            "\n"
            "Exploring encompasses both moving, exiting, or entering. "
            "Set explore_direction to be the player's direction which is either "
            "`left`, `right`, `forward`, or `backward`.  "
            "If the player's command doesn't specify "
            "the direction, then use `forward` by default.  "
            "If a player refers to exiting a room, they are indicating that "
            "they want to move forward through the only door.  "
            "For `open_chest`, set chest_side to `left` or `right` only if the "
            "player's command says which chest to open; otherwise leave it unset."
        )
        result = self._router_agent.invoke(content)
        return {
            "intent": {
                "type": result.intent,
                "explore_direction": result.explore_direction,
                "chest_side": result.chest_side,
            }
        }

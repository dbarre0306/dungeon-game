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
            "Categorize the player's command as exactly one of these "
            "categories:\n"
            "- `explore`\n"
            "- `look`\n"
            "- `attack`\n"
            "- `shop`\n"
            "- `drink_potion`\n"
            "- `open_chest`\n"
            "- `multiple`: the command matches more than one category.\n"
            "- `unknown`: the command matches no category.\n"
            "\n"
            "Then set the fields for the category:\n"
            "- `explore` covers moving, exiting, or entering.\n"
            "  - Set explore_direction to `left`, `right`, `forward`, or "
            "`backward`.\n"
            "  - If the command doesn't specify a direction, use `forward`.\n"
            "  - Exiting a room means moving `forward` through the only door.\n"
            "- `open_chest`:\n"
            "  - Set chest_side to `left` or `right` only if the command says "
            "which chest to open; otherwise leave it unset.\n"
            "- `shop`:\n"
            "  - Set shop_item to `potion`, `sword` or `shield` only "
            "if the command says what to buy; otherwise leave it unset.\n"
            "  - A steel sword is `sword` and a reinforced or steel shield is "
            "`shield`.\n"
            "  - Set shop_quantity only if the command gives a number (e.g. "
            "`buy 2 bottles of potion` is 2); otherwise leave it unset."
        )
        result = self._router_agent.invoke(content)
        return {
            "intent": {
                "type": result.intent,
                "explore_direction": result.explore_direction,
                "chest_side": result.chest_side,
                "shop_item": result.shop_item,
                "shop_quantity": result.shop_quantity,
            }
        }

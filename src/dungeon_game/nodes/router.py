from typing import Any

from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.domain.intent import IntentType
from dungeon_game.game_state import GameState

_CATEGORIES: dict[IntentType, str] = {
    "explore": "- `explore`",
    "look": "- `look`",
    "attack": "- `attack`",
    "shop": "- `shop`",
    "drink_potion": "- `drink_potion`",
    "open_chest": "- `open_chest`",
    "multiple": "- `multiple`: the command matches more than one category.",
    "unknown": "- `unknown`: the command matches no category.",
}

_FIELD_INSTRUCTIONS: dict[IntentType, str] = {
    "explore": (
        "- `explore` covers moving, exiting, or entering.\n"
        "  - Set explore_direction to `left`, `right`, `forward`, or "
        "`backward`.\n"
        "  - If the command doesn't specify a direction, use `forward`.\n"
        "  - Exiting a room means moving `forward` through the only door."
    ),
    "open_chest": (
        "- `open_chest`:\n"
        "  - Set chest_side to `left` or `right` only if the command says "
        "which chest to open; otherwise leave it unset."
    ),
    "shop": (
        "- `shop`:\n"
        "  - Set shop_item_name to `potion`, `sword` or `shield` only "
        "if the command says what to buy; otherwise leave it unset.\n"
        "  - A steel sword is `sword` and a reinforced or steel shield is "
        "`shield`.\n"
        "  - Set shop_quantity only if the command gives a number (e.g. "
        "`buy 2 bottles of potion` is 2); otherwise leave it unset."
    ),
}


def _build_prompt(command: str, supported_intents: list[IntentType]) -> str:
    intents: list[IntentType] = [*supported_intents, "multiple", "unknown"]
    categories = "\n".join(_CATEGORIES[intent] for intent in intents)
    prompt = (
        f"Player command: {command}\n"
        "\n"
        "Categorize the player's command as exactly one of these "
        "categories:\n"
        f"{categories}"
    )
    field_instructions = [
        _FIELD_INSTRUCTIONS[intent]
        for intent in supported_intents
        if intent in _FIELD_INSTRUCTIONS
    ]
    if field_instructions:
        prompt += "\n\nThen set the fields for the category:\n" + "\n".join(
            field_instructions
        )
    return prompt


class RouterNode:
    def __init__(self, router_agent: RouterAgent):
        self._router_agent = router_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        supported_intents = state.player.get_supported_intents()
        content = _build_prompt(state.command, supported_intents)
        result = self._router_agent.invoke(content, supported_intents)
        return {
            "intent": {
                "type": result.intent,
                "explore_direction": result.explore_direction,
                "chest_side": result.chest_side,
                "shop_item_name": result.shop_item_name,
                "shop_quantity": result.shop_quantity,
            }
        }

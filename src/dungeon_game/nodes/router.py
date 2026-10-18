from typing import Any

from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.domain.command_text import quote_command
from dungeon_game.domain.intent import IntentType, ShopItemName
from dungeon_game.domain.rooms.combat_room import CombatRoom
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
}


_SHOP_ITEM_HINTS: dict[ShopItemName, str] = {
    "potion": "A potion is `potion`.",
    "sword": "A steel sword is `sword`.",
    "shield": "A reinforced or steel shield is `shield`.",
    "elder_staff": "An elder staff is `elder_staff`.",
}


def _attack_instructions(enemy_name: str | None) -> str:
    enemy = f"the {enemy_name}" if enemy_name else "the enemy"
    return (
        f"- `attack` is striking {enemy} in the room.\n"
        f"  - Set attack_target to `enemy` if the command attacks {enemy} "
        "or does not say who to attack, `self` if the player would hurt "
        "themself, or `other` for anyone or anything else.\n"
        "  - Set attack_target_name to the name the player gave what they "
        "attack (e.g. `rat`); leave it unset if they gave none or only said "
        "`it`, `the beast`, `the monster` or `the enemy`."
    )


def _shop_instructions(shop_items: list[ShopItemName]) -> str:
    names = ", ".join(f"`{item}`" for item in shop_items)
    hints = "\n".join(f"  - {_SHOP_ITEM_HINTS[item]}" for item in shop_items)
    return (
        "- `shop`:\n"
        f"  - Set shop_item_name to one of {names} only if the command says "
        "what to buy; otherwise leave it unset.\n"
        f"{hints}\n"
        "  - Set shop_quantity only if the command gives a number (e.g. "
        "`buy 2 bottles of potion` is 2); otherwise leave it unset."
    )


def _build_prompt(
    command: str,
    supported_intents: list[IntentType],
    shop_items: list[ShopItemName],
    enemy_name: str | None = None,
) -> str:
    intents: list[IntentType] = [*supported_intents, "multiple", "unknown"]
    categories = "\n".join(_CATEGORIES[intent] for intent in intents)
    prompt = (
        f"Player command: {quote_command(command)}\n"
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
    if "attack" in supported_intents:
        field_instructions.append(_attack_instructions(enemy_name))
    if "shop" in supported_intents:
        field_instructions.append(_shop_instructions(shop_items))
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
        shop_items = [m.type for m in state.player.get_supported_merchandise()]
        room = state.get_current_room()
        enemy = room.enemy if isinstance(room, CombatRoom) else None
        enemy_name = enemy.name if enemy is not None and not enemy.is_dead() else None
        content = _build_prompt(
            state.command, supported_intents, shop_items, enemy_name
        )
        result = self._router_agent.invoke(
            content, supported_intents, shop_items, enemy_name
        )
        return {
            "intent": {
                "type": result.intent,
                "explore_direction": result.explore_direction,
                "chest_side": result.chest_side,
                "shop_item_name": result.shop_item_name,
                "shop_quantity": result.shop_quantity,
            }
        }

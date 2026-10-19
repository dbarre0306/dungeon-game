from typing import Literal

from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.intent import Intent
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom


class ShopRoom(DungeonRoom):
    """Where the player trades with the merchant, who lives here."""

    type: Literal["shop_room"] = "shop_room"
    merchant: Merchant

    def _is_valid_room_intent(self, intent: Intent) -> tuple[bool, str | None]:
        if intent.is_shop():
            return self._is_valid_purchase(intent)
        if intent.is_explore():
            return self._is_valid_explore(intent)
        if intent.is_look():
            return (True, None)
        if intent.is_attack():
            return (
                False,
                "Tell the player that there is nothing here to attack. "
                "The merchant is peaceful.",
            )
        return (
            False,
            "Tell the player that you don't understand what they have asked.",
        )

    @staticmethod
    def _is_valid_purchase(intent: Intent) -> tuple[bool, str | None]:
        if intent.shop_item_name is None:
            return (
                False,
                "Tell the player that they must say what they want to buy "
                "from the merchant.",
            )
        if intent.get_shop_quantity() < 1:
            return (
                False,
                "Tell the player that they must buy at least one item.",
            )
        return (True, None)

    @staticmethod
    def _is_valid_explore(intent: Intent) -> tuple[bool, str | None]:
        if intent.is_explore_forward():
            return (True, None)
        return (
            False,
            "Tell the player that the only way out is forward through the passageway.",
        )

    def get_room_facts(self) -> list[str]:
        return [
            "There is an old merchant behind a two-wheeled wooden cart, "
            "and he is selling: ",
            *self.merchant.describe_inventory(),
            "The player does not have to buy anything.",
            "The player can only buy one item at a time.",
            "There is only one passageway forward.",
        ]

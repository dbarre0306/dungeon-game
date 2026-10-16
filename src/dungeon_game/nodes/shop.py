from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.intent import ShopItem
from dungeon_game.domain.rooms.shop_room import ShopRoom
from dungeon_game.game_state import GameState


class ShopNode:
    """The player buys from the merchant in the shop room. The purchase is all or
    nothing."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print(f"SHOP : {state.intent.get_shop_quantity} x {state.intent.shop_item}")
        room = state.get_current_room()
        is_valid, msg = room.is_valid_intent(state.intent)
        if not is_valid:
            return self._narrate(state, msg)
        if not isinstance(room, ShopRoom):
            raise TypeError("The room must be a ShopRoom")
        item = state.intent.shop_item
        quantity = state.intent.get_shop_quantity()
        refusal = self._refusal(room, state, item, quantity)
        if refusal is not None:
            return self._narrate(state, refusal)
        return self._buy(state, room, item, quantity)

    @staticmethod
    def _refusal(
        room: ShopRoom, state: GameState, item: ShopItem | None, quantity: int
    ) -> str | None:
        merchant = room.merchant
        if not merchant.has_item_in_stock(item):
            return "Tell the player that the merchant has none of that to sell."
        if not merchant.is_in_stock(item, quantity):
            return (
                f"Tell the player that the merchant only has "
                f"{merchant.quantity_of(item)} of {merchant.name_of(item)} left, so they can't buy "
                f"{quantity}."
            )
        total = merchant.total_price(item, quantity)
        if not state.player.can_afford(total):
            return (
                f"Tell the player that {quantity} of {merchant.name_of(item)} cost "
                f"{total} gold coins but they only have "
                f"{state.player.gold_coins}, so they cannot afford it."
            )
        return None

    def _buy(
        self, state: GameState, room: ShopRoom, item_type: ShopItem, quantity: int
    ) -> dict[str, Any]:
        merchant = room.merchant

        total_price = merchant.total_price(item_type, quantity)
        merchant, item = merchant.with_item_removed(item_type, quantity)
        player = state.player.with_purchased_item(item, quantity, total_price)

        index = state.player.current_room_index
        sold_state = state.model_copy(
            update={
                "player": player,
                "dungeon": state.dungeon.with_room_updated(
                    index,
                    merchant=merchant,
                ),
            }
        )
        narration = self._dungeon_master_agent.invoke(
            sold_state,
            f"The player bought {quantity} "
            f"{merchant.name_of(item)} from the merchant for {total_price} gold coins.",
        ).narration
        return {
            "player": sold_state.player,
            "dungeon": sold_state.dungeon.with_room_updated(index, history=[narration]),
            "narration": [narration],
        }

    def _narrate(self, state: GameState, msg: str) -> dict[str, Any]:
        response = self._dungeon_master_agent.invoke(state, msg)
        return {"narration": [response.narration]}

from __future__ import annotations

from abc import abstractmethod
from typing import Self

from dungeon_game.domain.actors.combatant import Combatant
from dungeon_game.domain.actors.merchant.merchandise import Merchandise
from dungeon_game.domain.intent import IntentType
from dungeon_game.domain.items.inventory_items import InventoryItem


class Player(Combatant):
    gold_coins: int
    current_room_index: int

    @abstractmethod
    def get_facts(self) -> list[str]: ...

    @abstractmethod
    def get_supported_intents(self) -> list[IntentType]:
        """The actions this player can take. The router adds `multiple` and
        `unknown` itself, so they are not listed here."""

    @abstractmethod
    def get_supported_merchandise(self) -> list[Merchandise]:
        """What a merchant can sell this player."""

    def can_afford(self, price: int) -> bool:
        return self.gold_coins >= price

    @abstractmethod
    def with_purchased_item(
        self, item: InventoryItem, quantity: int, price: int
    ) -> Self: ...

    def print(self):
        pass

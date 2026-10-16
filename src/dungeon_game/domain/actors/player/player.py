from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel

from dungeon_game.domain.actors.combatant import Combatant
from dungeon_game.domain.intent import ShopItem

if TYPE_CHECKING:
    from dungeon_game.domain.actors.player.warrior import Shield, Sword


class Player(Combatant):
    gold_coins: int
    current_room_index: int

    @abstractmethod
    def get_facts(self) -> list[str]: ...

    def can_afford(self, price: int) -> bool:
        return self.gold_coins >= price

    @abstractmethod
    def with_purchased_item(
        self, item: ShopItem, quantity: int, price: int
    ) -> Self: ...

    def print(self):
        pass

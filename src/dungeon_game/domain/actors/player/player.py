from abc import abstractmethod
from typing import Self

from pydantic import BaseModel

from dungeon_game.domain.actors.combatant import Combatant


class Potions(BaseModel):
    name: str = "Potions"
    health_points: int
    quantity: int


class Player(Combatant):
    max_health_points: int
    is_fighting: bool
    gold_coins: int
    potions: Potions
    current_room_index: int

    @abstractmethod
    def get_facts(self) -> str:
        pass

    @abstractmethod
    def get_weapon(self) -> str:
        pass

    def take_damage(self, points: int) -> Self:
        """Return a copy of the player that lost `points` health (never below zero).
        A player who dies stops fighting."""
        player = super().take_damage(points)
        return player.model_copy(update={"is_fighting": player.is_fighting and player.is_alive()})

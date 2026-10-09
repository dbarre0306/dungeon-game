from abc import abstractmethod

from pydantic import BaseModel

from dungeon_game.domain.actors.combatant import Combatant


class Potions(BaseModel):
    name: str = "Potions"
    health_points: int
    quantity: int


class Player(Combatant):
    gold_coins: int
    potions: Potions
    current_room_index: int

    @abstractmethod
    def get_facts(self) -> str: ...

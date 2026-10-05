from abc import abstractmethod

from pydantic import BaseModel


class Potions(BaseModel):
    name: str = "Potions"
    health_points: int
    quantity: int


class Player(BaseModel):
    max_health_points: int
    health_points: int
    is_fighting: bool
    gold_coins: int
    potions: Potions
    current_room_index: int
    hit_bonus: int

    @abstractmethod
    def get_facts(self) -> str:
        pass

    @abstractmethod
    def get_weapon(self) -> str:
        pass

    @abstractmethod
    def get_extra_weapon_damage(self) -> int:
        pass

    def is_alive(self) -> bool:
        return self.health_points > 0

    def is_dead(self) -> bool:
        return not self.is_alive()

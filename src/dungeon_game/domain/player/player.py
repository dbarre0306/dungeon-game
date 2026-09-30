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
    last_action: str | None = None

    @abstractmethod
    def get_weapon(self) -> str:
        pass

    @abstractmethod
    def get_extra_weapon_damage(self) -> int:
        pass

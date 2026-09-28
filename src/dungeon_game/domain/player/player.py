from pydantic import BaseModel


class Potions(BaseModel):
    name: str
    health_points: int
    quantity: int

    def __init__(self, health_points: int, quantity: int):
        super().__init__(name="Potions", health_points=health_points, quantity=quantity)


class Player(BaseModel):
    max_health_points: int
    health_points: int
    is_fighting: bool
    gold_coins: int
    potions: Potions
    current_room_index: int

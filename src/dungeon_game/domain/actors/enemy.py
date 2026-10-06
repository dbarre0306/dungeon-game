from pydantic import BaseModel


class Enemy(BaseModel):
    name: str
    description: str
    health_points: int
    hit_bonus: int
    damage_bonus: int = 0

    def is_alive(self) -> bool:
        return self.health_points > 0

    def is_dead(self) -> bool:
        return not self.is_alive()

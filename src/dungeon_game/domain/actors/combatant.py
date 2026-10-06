from abc import abstractmethod
from typing import Self

from pydantic import BaseModel


class Combatant(BaseModel):
    """Anything that can fight: it has health, a to-hit bonus, and damage modifiers."""

    max_health_points: int
    health_points: int
    hit_bonus: int
    is_fighting: bool = False

    @abstractmethod
    def get_extra_damage(self) -> int:
        pass

    def get_damage_reduction(self) -> int:
        return 0

    def take_damage(self, points: int) -> Self:
        """Return a copy that lost `points` health (never below zero).
        A combatant who dies stops fighting."""
        health_points = max(0, self.health_points - points)
        return self.model_copy(
            update={
                "health_points": health_points,
                "is_fighting": self.is_fighting and health_points > 0,
            }
        )

    def is_alive(self) -> bool:
        return self.health_points > 0

    def is_dead(self) -> bool:
        return not self.is_alive()

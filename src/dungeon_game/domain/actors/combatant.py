from abc import abstractmethod
from typing import Self

from pydantic import BaseModel


class Combatant(BaseModel):
    """Anything that can fight: it has health, a to-hit bonus, and damage modifiers."""

    health_points: int
    hit_bonus: int

    @abstractmethod
    def get_extra_damage(self) -> int:
        pass

    def get_damage_reduction(self) -> int:
        return 0

    def take_damage(self, points: int) -> Self:
        """Return a copy that lost `points` health (never below zero)."""
        return self.model_copy(update={"health_points": max(0, self.health_points - points)})

    def is_alive(self) -> bool:
        return self.health_points > 0

    def is_dead(self) -> bool:
        return not self.is_alive()

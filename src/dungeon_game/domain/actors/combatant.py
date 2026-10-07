from abc import ABC, abstractmethod
from typing import Self

from pydantic import BaseModel


class Combatant(BaseModel, ABC):
    """Anything that can fight: it has health, a to-hit bonus, and damage modifiers."""

    max_health_points: int
    health_points: int
    hit_bonus: int
    is_fighting: bool = False

    @abstractmethod
    def get_weapon(self) -> str:
        """The item this combatant carries, e.g. a sword or a staff."""

    def get_attack(self) -> str:
        """What actually does the damage, as it should appear in narration.
        Usually the weapon itself; a spellcaster's attack is the spell."""
        return self.get_weapon()

    @abstractmethod
    def get_extra_damage(self) -> int:
        ...

    def get_defense(self) -> str | None:
        """What protects this combatant from damage, as it should appear in
        narration (e.g. a shield), or None if nothing does."""
        return None

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

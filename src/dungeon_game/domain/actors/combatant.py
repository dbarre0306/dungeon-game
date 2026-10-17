from abc import ABC, abstractmethod
from typing import Self

from pydantic import BaseModel


class Combatant(BaseModel, ABC):
    """Anything that can fight: it has health, a to-hit bonus, and damage modifiers."""

    max_health_points: int
    health_points: int
    hit_bonus: int
    is_fighting: bool = False

    @property
    @abstractmethod
    def offensive_weapon(self) -> str:
        """The item this combatant carries, e.g. a sword or a staff."""

    @property
    def offensive_weapon_payload(self) -> str:
        """What actually does the damage, as it should appear in narration.
        Usually the weapon itself; a spellcaster's attack is the spell."""
        return self.offensive_weapon

    @property
    @abstractmethod
    def additional_offensive_weapon_damage(self) -> int: ...

    @property
    def defensive_weapon(self) -> str | None:
        """What protects this combatant from damage, as it should appear in
        narration (e.g. a shield), or None if nothing does."""
        return None

    @property
    def reduced_defensive_weapon_damage(self) -> int:
        return 0

    def with_defense_worn(self, absorbed: int) -> Self:
        """Return a copy whose defense wore down by the `absorbed` damage points
        it just blocked. Nothing wears by default."""
        return self

    def describe_defense_change(self, before: Self) -> str | None:
        """What happened to the defense since `before`, as it should appear in
        narration (e.g. a shield broke), or None if its condition is unchanged."""
        return None

    def with_damage(self, points: int) -> Self:
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

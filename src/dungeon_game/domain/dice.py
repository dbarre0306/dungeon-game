import random


class Dice:
    """Rolls dice; inject a seeded `random.Random` to make rolls deterministic."""

    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def roll(self, num_sides: int) -> int:
        return self._rng.randint(1, num_sides)

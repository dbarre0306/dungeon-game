"""A shield blocks fully while good, half (but at least 1 point) while damaged, and
nothing once broken. Its defensive health points must be more than 1."""

import pytest
from pydantic import ValidationError

from dungeon_game.domain.items.inventory_items import Shield


def make_shield(defensive_health_points: int = 4, durability: int = 10) -> Shield:
    return Shield(
        name="test shield",
        defensive_health_points=defensive_health_points,
        max_durability=10,
        durability=durability,
    )


def test_good_shield_blocks_all_its_defensive_points():
    assert make_shield(4, durability=10).block_points == 4


def test_damaged_shield_blocks_half_its_defensive_points():
    shield = make_shield(4, durability=5)

    assert shield.condition == "damaged"
    assert shield.block_points == 2


def test_damaged_shield_with_odd_points_rounds_down():
    assert make_shield(5, durability=5).block_points == 2


def test_damaged_shield_with_smallest_allowed_points_still_blocks_one():
    shield = make_shield(2, durability=5)

    assert shield.condition == "damaged"
    assert shield.block_points == 1


def test_damaged_shield_blocks_no_more_than_its_remaining_durability():
    shield = make_shield(4, durability=1)

    assert shield.condition == "damaged"
    assert shield.block_points == 1


def test_good_shield_blocks_no_more_than_its_remaining_durability():
    shield = Shield(
        name="test shield",
        defensive_health_points=4,
        max_durability=4,
        durability=3,
    )

    assert shield.condition == "good"
    assert shield.block_points == 3


def test_broken_shield_blocks_nothing():
    shield = make_shield(4, durability=0)

    assert shield.condition == "broken"
    assert shield.block_points == 0


@pytest.mark.parametrize("points", [1, 0, -3])
def test_defensive_points_must_be_more_than_one(points):
    with pytest.raises(ValidationError):
        make_shield(points)


def test_defensive_points_of_two_are_allowed():
    assert make_shield(2).defensive_health_points == 2

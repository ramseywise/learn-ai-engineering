"""
Provides ship definitions and standard fleet configurations.
get_test_fleet() is useful when developing your Solver.
"""

from typing import List, NamedTuple


class Ship(NamedTuple):
    name: str
    size: int


def get_standard_fleet() -> List[Ship]:
    return [
        Ship("Carrier", 5),
        Ship("Battleship", 4),
        Ship("Cruiser", 3),
        Ship("Submarine", 3),
        Ship("Destroyer", 2),
    ]


def get_test_fleet() -> List[Ship]:
    return [
        Ship("Cruiser", 3),
        Ship("Submarine", 3),
    ]

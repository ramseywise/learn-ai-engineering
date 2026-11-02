"""Read this first."""

from enum import Enum
from typing import Dict, List, Set, Tuple

from sisyphus.drills.coding.battleship.src.fleet import Ship


class ShotResult(Enum):
    HIT = "HIT"
    MISS = "MISS"
    SUNK = "SUNK"


class Board:
    def __init__(self, grid_size: int = 10):
        self._grid_size = grid_size
        self._ships: Dict[str, List[Tuple[int, int]]] = {}
        self._hits: Set[Tuple[int, int]] = set()
        self._misses: Set[Tuple[int, int]] = set()
        self._occupied: Set[Tuple[int, int]] = set()
        self._sunk: Set[str] = set()

    @property
    def grid_size(self) -> int:
        return self._grid_size

    def place_ship(self, ship: Ship, row: int, col: int, horizontal: bool) -> None:
        cells: List[Tuple[int, int]] = []
        for i in range(ship.size):
            if horizontal:
                r, c = row, col + i
            else:
                r, c = row, col + i
            if r < 0 or r >= self._grid_size or c < 0 or c >= self._grid_size:
                raise ValueError(f"{ship.name} out of bounds at ({r}, {c})")
            if (r, c) in self._occupied:
                raise ValueError(f"{ship.name} overlaps at ({r}, {c})")
            cells.append((r, c))

        for cell in cells:
            self._occupied.add(cell)
        self._ships[ship.name] = cells

    def check_shot(self, row: int, col: int) -> ShotResult:
        if (row, col) in self._hits or (row, col) in self._misses:
            return ShotResult.MISS

        if (row, col) not in self._occupied:
            self._misses.add((row, col))
            return ShotResult.MISS

        self._hits.add((row, col))

        for name, cells in self._ships.items():
            if (row, col) in cells and name not in self._sunk:
                hit_count = sum(1 for c in cells[1:] if c in self._hits)
                if hit_count == len(cells) - 1:
                    self._sunk.add(name)
                    return ShotResult.SUNK
                return ShotResult.HIT

        return ShotResult.HIT

    def all_sunk(self) -> bool:
        return len(self._sunk) == len(self._ships)

    def remaining_ships(self) -> int:
        return len(self._ships) - len(self._sunk)

    def total_shots(self) -> int:
        return len(self._hits) + len(self._misses)

"""You'll implement this."""

from typing import List, Tuple

from programming.drills.coding.battleship.src.board import Board


class Solver:
    """Sinks all ships on a Battleship board."""

    def __init__(self, board: Board):
        self.board = board
        self.shots: List[Tuple[int, int]] = []

    def solve(self) -> None:
        pass

    def get_shots(self) -> List[Tuple[int, int]]:
        return self.shots

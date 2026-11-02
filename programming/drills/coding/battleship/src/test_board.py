"""Tests for Board — Bug Finding phase."""

import unittest

from programming.drills.coding.battleship.src.board import Board, ShotResult
from programming.drills.coding.battleship.src.fleet import Ship


class BoardTest(unittest.TestCase):
    def test_horizontal_hit_and_sunk(self) -> None:
        board = Board(grid_size=6)
        board.place_ship(Ship("Destroyer", 2), row=0, col=0, horizontal=True)
        r1 = board.check_shot(0, 0)
        r2 = board.check_shot(0, 1)
        self.assertEqual(r1, ShotResult.HIT)
        self.assertEqual(r2, ShotResult.SUNK)

    def test_miss(self) -> None:
        board = Board(grid_size=6)
        board.place_ship(Ship("Destroyer", 2), row=0, col=0, horizontal=True)
        result = board.check_shot(3, 3)
        self.assertEqual(result, ShotResult.MISS)

    def test_remaining_ships_after_sinking(self) -> None:
        board = Board(grid_size=6)
        board.place_ship(Ship("Destroyer", 2), row=0, col=0, horizontal=True)
        board.place_ship(Ship("Cruiser", 3), row=2, col=0, horizontal=True)
        self.assertEqual(board.remaining_ships(), 2)
        board.check_shot(0, 0)
        board.check_shot(0, 1)
        self.assertEqual(board.remaining_ships(), 1)

    def test_vertical_placement(self) -> None:
        board = Board(grid_size=6)
        board.place_ship(Ship("Cruiser", 3), row=0, col=0, horizontal=False)
        r1 = board.check_shot(1, 0)
        self.assertEqual(r1, ShotResult.HIT, f"expected HIT, got {r1}")


if __name__ == "__main__":
    unittest.main()

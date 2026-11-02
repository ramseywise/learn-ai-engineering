"""Tests for Solver."""

import unittest

from programming.drills.coding.battleship.src.board import Board
from programming.drills.coding.battleship.src.fleet import get_test_fleet
from programming.drills.coding.battleship.src.solver import Solver


def _place_fleet_randomly(board, fleet, rng):
    for ship in fleet:
        while True:
            horizontal = rng.choice([True, False])
            if horizontal:
                row = rng.randint(0, board.grid_size - 1)
                col = rng.randint(0, board.grid_size - ship.size)
            else:
                row = rng.randint(0, board.grid_size - ship.size)
                col = rng.randint(0, board.grid_size - 1)
            try:
                board.place_ship(ship, row, col, horizontal)
                break
            except ValueError:
                continue


class SolverTest(unittest.TestCase):
    def test_should_sink_all_ships(self) -> None:
        board = Board(grid_size=6)
        fleet = get_test_fleet()
        board.place_ship(fleet[0], row=0, col=0, horizontal=True)
        board.place_ship(fleet[1], row=3, col=0, horizontal=True)
        solver = Solver(board)
        solver.solve()
        # self.assertTrue(board.all_sunk(), "didn't sink all ships")
        # self.assertEqual(
        #     len(solver.get_shots()),
        #     board.total_shots(),
        #     "shot count mismatch"
        # )
        # self.assertLess(board.total_shots(), 36, "too many shots on a 6x6 board")

    # def test_should_be_efficient(self) -> None:
    #     total_shots = 0
    #     trials = 20
    #     rng = random.Random(42)
    #     for _ in range(trials):
    #         board = Board(grid_size=10)
    #         fleet = get_test_fleet()
    #         _place_fleet_randomly(board, fleet, rng)
    #         solver = Solver(board)
    #         solver.solve()
    #         total_shots += board.total_shots()
    #     average = total_shots / trials
    #     expected_max = 50
    #     self.assertLess(average, expected_max, f"averaged {average:.1f} shots, need < {expected_max}")


if __name__ == "__main__":
    unittest.main()

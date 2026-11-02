"""
Runs your Solver. It's useful to see how Solver is called.
You may want to change how Solver is constructed.
"""

from sisyphus.drills.coding.battleship.src.board import Board
from sisyphus.drills.coding.battleship.src.fleet import get_test_fleet
from programming.drills.coding.battleship.src.solver import Solver


def banner(legend: str) -> None:
    border = "#" * (len(legend) + 8)
    print(border)
    print(f"#   {legend}   #")
    print(border)


def main() -> None:
    banner("BEGIN CODE OUTPUT")

    board = Board(grid_size=6)
    fleet = get_test_fleet()
    board.place_ship(fleet[0], row=0, col=0, horizontal=True)
    board.place_ship(fleet[1], row=3, col=0, horizontal=True)

    solver = Solver(board)
    solver.solve()

    for row, col in solver.get_shots():
        print(f"  ({row},{col})")
    if board.all_sunk():
        print(f"WIN in {board.total_shots()} shots!")
    else:
        print(f"LOSS — {board.remaining_ships()} ships remaining")

    banner("END CODE OUTPUT")


if __name__ == "__main__":
    main()

import pandas as pd
def string_to_board(puzzle):
    board = []
    for row in range(9):
        current = []
        for col in range(9):
            current.append(
                int(
                    puzzle[row * 9 + col]
                )
            )
        board.append(current)
    return board


def load_puzzle(puzzle_id):
    df = pd.read_csv("data/output/puzzles.csv")
    row = df[df["id"] == puzzle_id].iloc[0]
    puzzle = string_to_board(row["puzzle"])
    solution = string_to_board(row["solution"])
    return puzzle, solution
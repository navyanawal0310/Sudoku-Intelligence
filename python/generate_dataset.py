#!/usr/bin/env python3
"""
generate_dataset.py

Generates a benchmarking dataset for the Sudoku Intelligence Lab project.

Produces 1000 unique Sudoku puzzles (250 Easy, 250 Medium, 250 Hard,
250 Expert) using the "dokusan" library (pip install dokusan) and writes
them to:

    data/dataset/sudoku_dataset.csv

CSV format:
    id,puzzle
    1,530070000600195000098000060800060003400803001700020006060000280000419005000080079

Run with:
    python python/generate_dataset.py
"""

import os
import csv

from dokusan import generators

OUTPUT_DIR = os.path.join("data", "dataset")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sudoku_dataset.csv")

TOTAL_PUZZLES = 1000
PUZZLES_PER_DIFFICULTY = 250

# Difficulty label -> dokusan avg_rank (higher rank == harder puzzle,
# based on the logical-technique difficulty scoring used by dokusan)
DIFFICULTY_LEVELS = {
    "Easy": 50,
    "Medium": 150,
    "Hard": 250,
    "Expert": 350,
}


def generate_puzzle_string(avg_rank):
    """Generate a single Sudoku puzzle string for the given difficulty rank."""
    sudoku = generators.random_sudoku(avg_rank=avg_rank)
    puzzle_string = str(sudoku).strip()
    return puzzle_string


def generate_unique_puzzles(avg_rank, count, seen, progress_counter):
    """Generate `count` unique puzzle strings for a given difficulty rank."""
    puzzles = []

    while len(puzzles) < count:
        puzzle_string = generate_puzzle_string(avg_rank)

        if len(puzzle_string) != 81:
            continue

        if puzzle_string in seen:
            continue

        seen.add(puzzle_string)
        puzzles.append(puzzle_string)

        progress_counter[0] += 1
        if progress_counter[0] % 100 == 0:
            print(f"Generated {progress_counter[0]} puzzles...")

    return puzzles


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    seen_puzzles = set()
    progress_counter = [0]

    all_rows = []
    puzzle_id = 1

    for difficulty_label, avg_rank in DIFFICULTY_LEVELS.items():
        puzzles = generate_unique_puzzles(
            avg_rank,
            PUZZLES_PER_DIFFICULTY,
            seen_puzzles,
            progress_counter,
        )

        for puzzle_string in puzzles:
            all_rows.append((puzzle_id, puzzle_string))
            puzzle_id += 1

    with open(OUTPUT_FILE, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["id", "puzzle"])
        for row_id, puzzle_string in all_rows:
            writer.writerow([row_id, puzzle_string])

    print(f"Total puzzles generated: {len(all_rows)}")
    print(f"Dataset written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
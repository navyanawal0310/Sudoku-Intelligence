import math
from collections import Counter


SIZE = 9
DIGITS = set(range(1, 10))


def parse_puzzle(puzzle: str):
    """Convert an 81-character puzzle string into a 9x9 grid."""

    puzzle = puzzle.strip()

    if len(puzzle) != 81:
        raise ValueError("Puzzle must contain exactly 81 characters.")

    if not all(ch in "0123456789" for ch in puzzle):
        raise ValueError("Puzzle may contain only digits 0-9.")

    return [
        [int(puzzle[r * SIZE + c]) for c in range(SIZE)]
        for r in range(SIZE)
    ]


def legal_candidates(grid, row, col):
    """Return the currently legal candidates for an empty cell."""

    if grid[row][col] != 0:
        return set()

    used = set(grid[row])

    used.update(grid[r][col] for r in range(SIZE))

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            used.add(grid[r][c])

    return DIGITS - used


def extract_candidate_features(puzzle: str):
    """
    Extract static candidate-domain features.

    IMPORTANT:
    No recursive search is performed here.
    """

    grid = parse_puzzle(puzzle)

    domain_sizes = []

    for row in range(SIZE):
        for col in range(SIZE):

            if grid[row][col] == 0:

                candidates = legal_candidates(grid, row, col)

                domain_sizes.append(len(candidates))

    empty_cells = len(domain_sizes)
    clue_count = 81 - empty_cells

    if empty_cells == 0:
        return {
            "clue_count": 81,
            "empty_cells": 0,
            "mean_domain_size": 0.0,
            "domain_variance": 0.0,
            "min_domain_size": 0,
            "max_domain_size": 0,
            "singleton_count": 0,
            "singleton_ratio": 0.0,
            "pair_count": 0,
            "pair_ratio": 0.0,
            "triple_count": 0,
            "triple_ratio": 0.0,
            "candidate_domain_entropy": 0.0,
        }

    counts = Counter(domain_sizes)

    mean_domain = sum(domain_sizes) / empty_cells

    variance = (
        sum((d - mean_domain) ** 2 for d in domain_sizes)
        / empty_cells
    )

    singleton_count = counts[1]
    pair_count = counts[2]
    triple_count = counts[3]

    candidate_domain_entropy = (
        sum(math.log2(d) for d in domain_sizes if d > 0)
        / empty_cells
    )

    return {
        "clue_count": clue_count,
        "empty_cells": empty_cells,

        "mean_domain_size": mean_domain,
        "domain_variance": variance,

        "min_domain_size": min(domain_sizes),
        "max_domain_size": max(domain_sizes),

        "singleton_count": singleton_count,
        "singleton_ratio": singleton_count / empty_cells,

        "pair_count": pair_count,
        "pair_ratio": pair_count / empty_cells,

        "triple_count": triple_count,
        "triple_ratio": triple_count / empty_cells,

        "candidate_domain_entropy": candidate_domain_entropy,
    }
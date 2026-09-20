from candidate_features import (
    SIZE,
    parse_puzzle,
    legal_candidates,
)


def count_empty_cells(grid):
    """Count unassigned cells."""

    return sum(
        1
        for row in grid
        for value in row
        if value == 0
    )


def candidate_summary(grid):
    """
    Summarize candidate domains on the current board.

    Returns:
        mean candidate-domain size
        number of singleton domains
        number of zero-candidate domains
    """

    domain_sizes = []

    for row in range(SIZE):
        for col in range(SIZE):

            if grid[row][col] == 0:

                candidates = legal_candidates(
                    grid,
                    row,
                    col
                )

                domain_sizes.append(
                    len(candidates)
                )

    if not domain_sizes:
        return 0.0, 0, 0

    mean_domain = (
        sum(domain_sizes)
        / len(domain_sizes)
    )

    singleton_count = sum(
        1
        for size in domain_sizes
        if size == 1
    )

    zero_domain_count = sum(
        1
        for size in domain_sizes
        if size == 0
    )

    return (
        mean_domain,
        singleton_count,
        zero_domain_count,
    )


def propagate_naked_singles(puzzle):
    """
    Apply synchronous naked-single propagation.

    No guessing.
    No recursive search.
    No backtracking.

    All naked singles identified during a round
    are computed from the same board state before
    any of them are applied.
    """

    grid = parse_puzzle(puzzle)

    initial_empty = count_empty_cells(grid)

    (
        initial_mean_domain,
        initial_singletons,
        initial_zero_domains,
    ) = candidate_summary(grid)

    forced_assignments = 0
    propagation_rounds = 0
    contradiction = (
        initial_zero_domains > 0
    )

    while not contradiction:

        forced_moves = []

        # Discover all naked singles using the
        # unchanged board for this round.
        for row in range(SIZE):
            for col in range(SIZE):

                if grid[row][col] != 0:
                    continue

                candidates = legal_candidates(
                    grid,
                    row,
                    col
                )

                if len(candidates) == 0:
                    contradiction = True
                    break

                if len(candidates) == 1:

                    value = next(
                        iter(candidates)
                    )

                    forced_moves.append(
                        (row, col, value)
                    )

            if contradiction:
                break

        if contradiction:
            break

        if not forced_moves:
            break

        # Apply the entire round simultaneously.
        for row, col, value in forced_moves:
            grid[row][col] = value

        forced_assignments += len(
            forced_moves
        )

        propagation_rounds += 1

        # Validate that simultaneous assignments
        # have not created conflicting givens.
        if not grid_is_consistent(grid):
            contradiction = True
            break

    residual_empty = count_empty_cells(grid)

    (
        final_mean_domain,
        final_singletons,
        final_zero_domains,
    ) = candidate_summary(grid)

    if final_zero_domains > 0:
        contradiction = True

    reduction_ratio = (
        forced_assignments / initial_empty
        if initial_empty > 0
        else 0.0
    )

    solved_by_propagation = (
        residual_empty == 0
        and not contradiction
    )

    return {
        "prop_initial_empty":
            initial_empty,

        "prop_initial_singletons":
            initial_singletons,

        "prop_forced_assignments":
            forced_assignments,

        "prop_rounds":
            propagation_rounds,

        "prop_reduction_ratio":
            reduction_ratio,

        "prop_residual_empty":
            residual_empty,

        "prop_initial_mean_domain":
            initial_mean_domain,

        "prop_final_mean_domain":
            final_mean_domain,

        "prop_final_singletons":
            final_singletons,

        "prop_contradiction":
            int(contradiction),

        "prop_solved":
            int(solved_by_propagation),
    }


def grid_is_consistent(grid):
    """
    Check rows, columns and boxes for duplicate
    non-zero values.
    """

    # Rows
    for row in grid:

        values = [
            value
            for value in row
            if value != 0
        ]

        if len(values) != len(set(values)):
            return False

    # Columns
    for col in range(SIZE):

        values = [
            grid[row][col]
            for row in range(SIZE)
            if grid[row][col] != 0
        ]

        if len(values) != len(set(values)):
            return False

    # Boxes
    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):

            values = []

            for row in range(
                box_row,
                box_row + 3
            ):
                for col in range(
                    box_col,
                    box_col + 3
                ):

                    value = grid[row][col]

                    if value != 0:
                        values.append(value)

            if len(values) != len(set(values)):
                return False

    return True
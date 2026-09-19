import csv
import math
from pathlib import Path


STRUCTURAL_FILE = Path(
    "research/results/structural_features_100.csv"
)

SOLVER_FILE = Path(
    "research/results/solver_runs_100.csv"
)

PUZZLE_FILE = Path(
    "research/data/pilot/puzzles_100.csv"
)

OUTPUT_FILE = Path(
    "research/results/analysis_dataset_100.csv"
)


def read_csv_by_id(path):
    """Read a CSV and index rows by puzzle_id."""

    with path.open(
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        rows = {}

        for row in reader:

            puzzle_id = row["puzzle_id"]

            if puzzle_id in rows:
                raise ValueError(
                    f"Duplicate puzzle_id in {path}: "
                    f"{puzzle_id}"
                )

            rows[puzzle_id] = row

        return rows


def validate_solver_invariants(row):
    """
    Validate deterministic instrumentation identities
    for BT_NAIVE.
    """

    recursive_calls = int(
        row["recursive_calls"]
    )

    candidate_checks = int(
        row["candidate_checks"]
    )

    constraint_rejections = int(
        row["constraint_rejections"]
    )

    committed_assignments = int(
        row["committed_assignments"]
    )

    backtracked_assignments = int(
        row["backtracked_assignments"]
    )

    search_nodes = int(
        row["search_nodes"]
    )

    solution_depth = int(
        row["solution_depth"]
    )

    checks = {
        "candidate_partition":
            candidate_checks
            ==
            constraint_rejections
            + committed_assignments,

        "recursive_identity":
            recursive_calls
            ==
            committed_assignments + 1,

        "solution_path_identity":
            committed_assignments
            - backtracked_assignments
            ==
            solution_depth,

        "node_identity":
            search_nodes
            ==
            recursive_calls,
    }

    return checks


def main():

    puzzles = read_csv_by_id(
        PUZZLE_FILE
    )

    structural = read_csv_by_id(
        STRUCTURAL_FILE
    )

    solver = read_csv_by_id(
        SOLVER_FILE
    )

    puzzle_ids = set(puzzles)
    structural_ids = set(structural)
    solver_ids = set(solver)

    print("Dataset alignment")
    print("-----------------")
    print("Puzzle records     :", len(puzzle_ids))
    print("Structural records :", len(structural_ids))
    print("Solver records     :", len(solver_ids))
    print()

    if puzzle_ids != structural_ids:
        missing = puzzle_ids - structural_ids

        raise RuntimeError(
            "Structural dataset does not match "
            f"puzzle dataset. Missing: {missing}"
        )

    if puzzle_ids != solver_ids:
        missing = puzzle_ids - solver_ids

        raise RuntimeError(
            "Solver dataset does not match "
            f"puzzle dataset. Missing: {missing}"
        )

    invariant_failures = []

    invalid_solutions = []

    output_rows = []

    for puzzle_id in sorted(puzzle_ids):

        puzzle = puzzles[puzzle_id]
        features = structural[puzzle_id]
        run = solver[puzzle_id]

        solved = int(run["solved"])
        solution_valid = int(
            run["solution_valid"]
        )

        if not solved or not solution_valid:
            invalid_solutions.append(
                puzzle_id
            )

        checks = validate_solver_invariants(
            run
        )

        failed = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        if failed:
            invariant_failures.append(
                (puzzle_id, failed)
            )

        recursive_calls = int(
            run["recursive_calls"]
        )

        backtracked_assignments = int(
            run["backtracked_assignments"]
        )

        candidate_checks = int(
            run["candidate_checks"]
        )

        # Primary transformed complexity target.
        log_recursive_calls = math.log1p(
            recursive_calls
        )

        row = {}

        # Provenance / identity
        row["puzzle_id"] = puzzle_id

        row["source"] = puzzle[
            "source"
        ]

        row["source_record_id"] = puzzle[
            "source_record_id"
        ]

        row["source_difficulty"] = puzzle[
            "source_difficulty"
        ]

        row["sampling_seed"] = puzzle[
            "sampling_seed"
        ]

        # Pre-solve structural features
        for key, value in features.items():

            if key != "puzzle_id":
                row[key] = value

        # Search-dynamics outcomes
        row["recursive_calls"] = (
            recursive_calls
        )

        row["log_recursive_calls"] = (
            log_recursive_calls
        )

        row["backtracked_assignments"] = (
            backtracked_assignments
        )

        row["candidate_checks"] = (
            candidate_checks
        )

        row["backtrack_events"] = (
            run["backtrack_events"]
        )

        row["max_depth"] = (
            run["max_depth"]
        )

        row["solution_depth"] = (
            run["solution_depth"]
        )

        row["solved"] = solved

        row["solution_valid"] = (
            solution_valid
        )

        output_rows.append(row)

    print("Validation")
    print("----------")

    print(
        "Invalid solutions :",
        len(invalid_solutions)
    )

    print(
        "Invariant failures:",
        len(invariant_failures)
    )

    if invalid_solutions:
        print(
            "Invalid:",
            invalid_solutions
        )

    if invariant_failures:

        for puzzle_id, failures in (
            invariant_failures
        ):
            print(
                puzzle_id,
                failures
            )

    if invalid_solutions:
        raise RuntimeError(
            "One or more solver outputs "
            "are invalid."
        )

    if invariant_failures:
        raise RuntimeError(
            "Instrumentation invariant "
            "failure detected."
        )

    if len(output_rows) != 100:
        raise RuntimeError(
            f"Expected 100 rows, "
            f"found {len(output_rows)}."
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = list(
        output_rows[0].keys()
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(output_rows)

    print()
    print("PASS: experiment integrity verified.")
    print()
    print(
        "Analysis dataset:",
        OUTPUT_FILE
    )

    print(
        "Rows:",
        len(output_rows)
    )


if __name__ == "__main__":
    main()
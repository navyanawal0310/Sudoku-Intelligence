import csv
import math
import statistics
from pathlib import Path


NAIVE_PATH = Path("research/results/solver_runs_100.csv")
MRV_PATH = Path("research/results/solver_runs_mrv_100.csv")
OUTPUT_PATH = Path("research/results/solver_sensitivity_100.csv")


def load_runs(path):
    records = {}

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            puzzle_id = row["puzzle_id"]

            if puzzle_id in records:
                raise ValueError(
                    f"Duplicate puzzle_id {puzzle_id} in {path}"
                )

            records[puzzle_id] = row

    return records


def validate_run(row, expected_solver):
    puzzle_id = row["puzzle_id"]

    if row["solver"] != expected_solver:
        raise ValueError(
            f"{puzzle_id}: expected solver {expected_solver}, "
            f"found {row['solver']}"
        )

    if int(row["solved"]) != 1:
        raise ValueError(f"{puzzle_id}: puzzle not solved")

    if int(row["solution_valid"]) != 1:
        raise ValueError(f"{puzzle_id}: invalid solution")

    recursive_calls = int(row["recursive_calls"])
    candidate_checks = int(row["candidate_checks"])
    constraint_rejections = int(row["constraint_rejections"])
    committed = int(row["committed_assignments"])
    backtracked = int(row["backtracked_assignments"])
    search_nodes = int(row["search_nodes"])
    solution_depth = int(row["solution_depth"])

    if candidate_checks != constraint_rejections + committed:
        raise ValueError(
            f"{puzzle_id}: candidate accounting invariant failed"
        )

    if recursive_calls != committed + 1:
        raise ValueError(
            f"{puzzle_id}: recursive-call invariant failed"
        )

    if committed - backtracked != solution_depth:
        raise ValueError(
            f"{puzzle_id}: assignment invariant failed"
        )

    if search_nodes != recursive_calls:
        raise ValueError(
            f"{puzzle_id}: search-node invariant failed"
        )


def percentile(values, p):
    ordered = sorted(values)

    if not ordered:
        raise ValueError("Cannot calculate percentile of empty data")

    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    fraction = position - lower

    return (
        ordered[lower] * (1 - fraction)
        + ordered[upper] * fraction
    )


def rank_values(values):
    """
    Average ranks for ties.
    Rank 1 corresponds to the smallest value.
    """

    indexed = sorted(
        enumerate(values),
        key=lambda item: item[1]
    )

    ranks = [0.0] * len(values)

    i = 0

    while i < len(indexed):
        j = i

        while (
            j + 1 < len(indexed)
            and indexed[j + 1][1] == indexed[i][1]
        ):
            j += 1

        average_rank = (i + j + 2) / 2.0

        for k in range(i, j + 1):
            original_index = indexed[k][0]
            ranks[original_index] = average_rank

        i = j + 1

    return ranks


def pearson(x, y):
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    numerator = sum(
        (a - mean_x) * (b - mean_y)
        for a, b in zip(x, y)
    )

    denominator_x = math.sqrt(
        sum((a - mean_x) ** 2 for a in x)
    )

    denominator_y = math.sqrt(
        sum((b - mean_y) ** 2 for b in y)
    )

    if denominator_x == 0 or denominator_y == 0:
        return float("nan")

    return numerator / (denominator_x * denominator_y)


def spearman(x, y):
    return pearson(
        rank_values(x),
        rank_values(y)
    )


def main():
    naive = load_runs(NAIVE_PATH)
    mrv = load_runs(MRV_PATH)

    naive_ids = set(naive)
    mrv_ids = set(mrv)

    if naive_ids != mrv_ids:
        only_naive = sorted(naive_ids - mrv_ids)
        only_mrv = sorted(mrv_ids - naive_ids)

        raise ValueError(
            "Puzzle ID mismatch.\n"
            f"Only NAIVE: {only_naive}\n"
            f"Only MRV: {only_mrv}"
        )

    puzzle_ids = sorted(naive_ids)

    rows = []

    naive_calls = []
    mrv_calls = []
    ratios = []
    ssi_values = []

    mrv_better = 0
    equal = 0
    mrv_worse = 0

    for puzzle_id in puzzle_ids:
        n = naive[puzzle_id]
        m = mrv[puzzle_id]

        validate_run(n, "BT_NAIVE")
        validate_run(m, "BT_MRV")

        # Verify that both observations refer to the same puzzle metadata.
        for field in [
            "source",
            "source_difficulty",
            "clue_count",
        ]:
            if n[field] != m[field]:
                raise ValueError(
                    f"{puzzle_id}: mismatch in {field}: "
                    f"{n[field]} vs {m[field]}"
                )

        n_calls = int(n["recursive_calls"])
        m_calls = int(m["recursive_calls"])

        ratio = n_calls / m_calls

        # Solver Sensitivity Index.
        #
        # Positive:
        #     NAIVE required more recursive calls.
        #
        # Zero:
        #     equal recursive-call cost.
        #
        # Negative:
        #     MRV required more recursive calls.
        ssi = math.log(
            (n_calls + 1) / (m_calls + 1)
        )

        if m_calls < n_calls:
            outcome = "MRV_BETTER"
            mrv_better += 1

        elif m_calls == n_calls:
            outcome = "EQUAL"
            equal += 1

        else:
            outcome = "MRV_WORSE"
            mrv_worse += 1

        naive_calls.append(n_calls)
        mrv_calls.append(m_calls)
        ratios.append(ratio)
        ssi_values.append(ssi)

        rows.append({
            "puzzle_id": puzzle_id,
            "source": n["source"],
            "source_difficulty": n["source_difficulty"],
            "clue_count": n["clue_count"],
            "naive_recursive_calls": n_calls,
            "mrv_recursive_calls": m_calls,
            "call_ratio_naive_over_mrv": f"{ratio:.8f}",
            "ssi_log_call_ratio": f"{ssi:.8f}",
            "outcome": outcome,
        })

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        fieldnames = [
            "puzzle_id",
            "source",
            "source_difficulty",
            "clue_count",
            "naive_recursive_calls",
            "mrv_recursive_calls",
            "call_ratio_naive_over_mrv",
            "ssi_log_call_ratio",
            "outcome",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    rho = spearman(
        naive_calls,
        mrv_calls
    )

    print()
    print("Build 4.3 - Paired Solver-Sensitivity Analysis")
    print("===============================================")
    print()

    print("Integrity")
    print("-----------------------------------------------")
    print(f"NAIVE records       : {len(naive)}")
    print(f"MRV records         : {len(mrv)}")
    print(f"Matched puzzle IDs  : {len(puzzle_ids)}")
    print("Solver invariants   : PASS")
    print("Metadata agreement  : PASS")
    print()

    print("Paired outcome")
    print("-----------------------------------------------")
    print(f"MRV better          : {mrv_better}")
    print(f"Equal               : {equal}")
    print(f"MRV worse           : {mrv_worse}")
    print()

    print("Recursive calls")
    print("-----------------------------------------------")
    print(
        f"NAIVE median        : "
        f"{statistics.median(naive_calls):.2f}"
    )
    print(
        f"MRV median          : "
        f"{statistics.median(mrv_calls):.2f}"
    )
    print()

    print("NAIVE / MRV call ratio")
    print("-----------------------------------------------")
    print(
        f"Minimum             : {min(ratios):.4f}"
    )
    print(
        f"Q1                  : {percentile(ratios, 0.25):.4f}"
    )
    print(
        f"Median              : {statistics.median(ratios):.4f}"
    )
    print(
        f"Q3                  : {percentile(ratios, 0.75):.4f}"
    )
    print(
        f"Maximum             : {max(ratios):.4f}"
    )
    print()

    print("Solver Sensitivity Index")
    print("-----------------------------------------------")
    print(
        f"Minimum SSI         : {min(ssi_values):.4f}"
    )
    print(
        f"Q1 SSI              : {percentile(ssi_values, 0.25):.4f}"
    )
    print(
        f"Median SSI          : {statistics.median(ssi_values):.4f}"
    )
    print(
        f"Q3 SSI              : {percentile(ssi_values, 0.75):.4f}"
    )
    print(
        f"Maximum SSI         : {max(ssi_values):.4f}"
    )
    print()

    print("Cross-solver difficulty ordering")
    print("-----------------------------------------------")
    print(
        f"Spearman rho        : {rho:.4f}"
    )
    print()

    print(
        f"Output written to   : {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
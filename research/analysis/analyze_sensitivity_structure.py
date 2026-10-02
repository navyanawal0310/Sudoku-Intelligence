import csv
import math
import statistics
from pathlib import Path


FEATURE_PATH = Path(
    "research/results/structural_features_100.csv"
)

SENSITIVITY_PATH = Path(
    "research/results/solver_sensitivity_100.csv"
)


FEATURES = [
    # Baseline density
    "empty_cells",

    # Static candidate structure
    "mean_domain_size",
    "domain_variance",
    "singleton_ratio",
    "pair_ratio",
    "triple_ratio",
    "candidate_domain_entropy",

    # Spatial clue structure
    "row_clue_variance",
    "column_clue_variance",
    "box_clue_variance",

    # Propagation response
    "prop_forced_assignments",
    "prop_rounds",
    "prop_reduction_ratio",
    "prop_residual_empty",
    "prop_final_mean_domain",
]


def load_csv(path):
    records = {}

    with path.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            puzzle_id = row["puzzle_id"]

            if puzzle_id in records:
                raise ValueError(
                    f"Duplicate puzzle ID: {puzzle_id}"
                )

            records[puzzle_id] = row

    return records


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

    return numerator / (
        denominator_x * denominator_y
    )


def rank_values(values):
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
            and indexed[j + 1][1]
            == indexed[i][1]
        ):
            j += 1

        average_rank = (
            i + j + 2
        ) / 2.0

        for k in range(i, j + 1):
            original_index = indexed[k][0]
            ranks[original_index] = average_rank

        i = j + 1

    return ranks


def spearman(x, y):
    return pearson(
        rank_values(x),
        rank_values(y)
    )


def main():

    features = load_csv(FEATURE_PATH)
    sensitivity = load_csv(SENSITIVITY_PATH)

    feature_ids = set(features)
    sensitivity_ids = set(sensitivity)

    if feature_ids != sensitivity_ids:

        only_features = sorted(
            feature_ids - sensitivity_ids
        )

        only_sensitivity = sorted(
            sensitivity_ids - feature_ids
        )

        raise ValueError(
            "Puzzle ID mismatch\n"
            f"Only features: {only_features}\n"
            f"Only sensitivity: {only_sensitivity}"
        )

    puzzle_ids = sorted(feature_ids)

    print()
    print(
        "Build 4.4 - Structure vs Solver Sensitivity"
    )
    print(
        "============================================"
    )
    print()

    print("Integrity")
    print("--------------------------------------------")
    print(
        f"Structural records  : {len(features)}"
    )
    print(
        f"Sensitivity records : {len(sensitivity)}"
    )
    print(
        f"Matched puzzle IDs  : {len(puzzle_ids)}"
    )
    print()

    ssi = [
        float(
            sensitivity[puzzle_id][
                "ssi_log_call_ratio"
            ]
        )
        for puzzle_id in puzzle_ids
    ]

    results = []

    for feature in FEATURES:

        values = [
            float(
                features[puzzle_id][feature]
            )
            for puzzle_id in puzzle_ids
        ]

        pearson_r = pearson(
            values,
            ssi
        )

        spearman_rho = spearman(
            values,
            ssi
        )

        results.append(
            (
                feature,
                pearson_r,
                spearman_rho
            )
        )

    results.sort(
        key=lambda row:
            abs(row[2]),
        reverse=True
    )

    print("Association with SSI")
    print("--------------------------------------------")
    print(
        f"{'Feature':30}"
        f"{'Pearson':>12}"
        f"{'Spearman':>12}"
    )

    for (
        feature,
        pearson_r,
        spearman_rho
    ) in results:

        print(
            f"{feature:30}"
            f"{pearson_r:12.4f}"
            f"{spearman_rho:12.4f}"
        )

    print()
    print("Extreme SSI puzzles")
    print("--------------------------------------------")

    ordered = sorted(
        puzzle_ids,
        key=lambda puzzle_id:
            float(
                sensitivity[puzzle_id][
                    "ssi_log_call_ratio"
                ]
            )
    )

    print()
    print("Lowest SSI:")
    print()

    for puzzle_id in ordered[:5]:

        row = sensitivity[puzzle_id]

        print(
            f"{puzzle_id:8} "
            f"SSI={float(row['ssi_log_call_ratio']):8.4f} "
            f"NAIVE={int(row['naive_recursive_calls']):8} "
            f"MRV={int(row['mrv_recursive_calls']):8} "
            f"{row['source_difficulty']}"
        )

    print()
    print("Highest SSI:")
    print()

    for puzzle_id in reversed(
        ordered[-5:]
    ):

        row = sensitivity[puzzle_id]

        print(
            f"{puzzle_id:8} "
            f"SSI={float(row['ssi_log_call_ratio']):8.4f} "
            f"NAIVE={int(row['naive_recursive_calls']):8} "
            f"MRV={int(row['mrv_recursive_calls']):8} "
            f"{row['source_difficulty']}"
        )

    print()
    print("MRV-worse cases")
    print("--------------------------------------------")

    worse = [
        puzzle_id
        for puzzle_id in puzzle_ids
        if sensitivity[puzzle_id]["outcome"]
        == "MRV_WORSE"
    ]

    for puzzle_id in worse:

        s = sensitivity[puzzle_id]
        f = features[puzzle_id]

        print()
        print(puzzle_id)
        print(
            f"  difficulty          : "
            f"{s['source_difficulty']}"
        )
        print(
            f"  SSI                 : "
            f"{float(s['ssi_log_call_ratio']):.4f}"
        )
        print(
            f"  NAIVE calls         : "
            f"{s['naive_recursive_calls']}"
        )
        print(
            f"  MRV calls           : "
            f"{s['mrv_recursive_calls']}"
        )
        print(
            f"  empty cells         : "
            f"{f['empty_cells']}"
        )
        print(
            f"  mean domain size    : "
            f"{float(f['mean_domain_size']):.4f}"
        )
        print(
            f"  domain entropy      : "
            f"{float(f['candidate_domain_entropy']):.4f}"
        )
        print(
            f"  singleton ratio     : "
            f"{float(f['singleton_ratio']):.4f}"
        )
        print(
            f"  propagation forced  : "
            f"{f['prop_forced_assignments']}"
        )
        print(
            f"  residual empty      : "
            f"{f['prop_residual_empty']}"
        )


if __name__ == "__main__":
    main()
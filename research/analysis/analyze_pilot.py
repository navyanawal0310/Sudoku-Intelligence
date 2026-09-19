import csv
import math
from pathlib import Path


INPUT = Path(
    "research/results/analysis_dataset_100.csv"
)


FEATURES = [
    "clue_count",
    "empty_cells",
    "mean_domain_size",
    "domain_variance",
    "singleton_ratio",
    "pair_ratio",
    "triple_ratio",
    "candidate_domain_entropy",
    "row_clue_variance",
    "column_clue_variance",
    "box_clue_variance",
]


def load_data():

    with INPUT.open(
        newline="",
        encoding="utf-8"
    ) as file:

        return list(csv.DictReader(file))


def pearson(x, y):

    n = len(x)

    mean_x = sum(x) / n
    mean_y = sum(y) / n

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

    denominator = (
        denominator_x * denominator_y
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


def main():

    rows = load_data()

    target = [
        float(row["log_recursive_calls"])
        for row in rows
    ]

    print()
    print("Pilot Structural-Search Analysis")
    print("================================")
    print(f"N = {len(rows)}")
    print()

    print(
        "Target: log(1 + recursive_calls)"
    )

    print()
    print(
        f"{'Feature':30s} {'Pearson r':>12s}"
    )

    print(
        f"{'-' * 30} {'-' * 12}"
    )

    results = []

    for feature in FEATURES:

        values = [
            float(row[feature])
            for row in rows
        ]

        r = pearson(
            values,
            target
        )

        results.append(
            (feature, r)
        )

    results.sort(
        key=lambda item: abs(item[1]),
        reverse=True
    )

    for feature, r in results:

        print(
            f"{feature:30s} {r:12.4f}"
        )

    # Search complexity summary
    calls = [
        int(row["recursive_calls"])
        for row in rows
    ]

    sorted_calls = sorted(calls)

    print()
    print("Search complexity")
    print("-----------------")

    print(
        "Minimum recursive calls :",
        min(calls)
    )

    print(
        "Median recursive calls  :",
        sorted_calls[len(calls) // 2]
    )

    print(
        "Maximum recursive calls :",
        max(calls)
    )

    print(
        "Mean recursive calls    :",
        round(sum(calls) / len(calls), 2)
    )

    # Complexity by external category
    print()
    print("External difficulty groups")
    print("--------------------------")

    categories = [
        "easy",
        "medium",
        "hard",
        "diabolical",
    ]

    for category in categories:

        category_calls = [
            int(row["recursive_calls"])
            for row in rows
            if row["source_difficulty"]
            == category
        ]

        category_logs = [
            math.log1p(value)
            for value in category_calls
        ]

        print(
            f"{category:10s}"
            f" n={len(category_calls):2d}"
            f" median_calls="
            f"{sorted(category_calls)[len(category_calls)//2]:8d}"
            f" mean_log_calls="
            f"{sum(category_logs)/len(category_logs):.3f}"
        )


if __name__ == "__main__":
    main()
import csv
from pathlib import Path


INPUT = Path(
    "research/results/analysis_dataset_100.csv"
)


def main():

    with INPUT.open(
        newline="",
        encoding="utf-8"
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    forced = [
        int(row["prop_forced_assignments"])
        for row in rows
    ]

    rounds = [
        int(row["prop_rounds"])
        for row in rows
    ]

    residual = [
        int(row["prop_residual_empty"])
        for row in rows
    ]

    contradictions = sum(
        int(row["prop_contradiction"])
        for row in rows
    )

    solved = sum(
        int(row["prop_solved"])
        for row in rows
    )

    print()
    print("Propagation Response Audit")
    print("==========================")
    print(f"N = {len(rows)}")
    print()

    print(
        "Contradictions       :",
        contradictions
    )

    print(
        "Solved by propagation:",
        solved
    )

    print()

    print(
        "Forced assignments"
    )

    print(
        "  minimum:",
        min(forced)
    )

    print(
        "  median :",
        sorted(forced)[len(forced) // 2]
    )

    print(
        "  maximum:",
        max(forced)
    )

    print()

    print(
        "Propagation rounds"
    )

    print(
        "  minimum:",
        min(rounds)
    )

    print(
        "  median :",
        sorted(rounds)[len(rounds) // 2]
    )

    print(
        "  maximum:",
        max(rounds)
    )

    print()

    print(
        "Residual empty cells"
    )

    print(
        "  minimum:",
        min(residual)
    )

    print(
        "  median :",
        sorted(residual)[len(residual) // 2]
    )

    print(
        "  maximum:",
        max(residual)
    )


if __name__ == "__main__":
    main()
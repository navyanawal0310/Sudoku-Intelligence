import csv
from pathlib import Path

from candidate_features import extract_candidate_features


INPUT = Path("research/data/pilot/puzzles.csv")

OUTPUT = Path(
    "research/results/structural_features.csv"
)


def main():

    rows = []

    with INPUT.open(newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for record in reader:

            features = extract_candidate_features(
                record["puzzle"]
            )

            features["puzzle_id"] = record["puzzle_id"]

            rows.append(features)

            print(
                record["puzzle_id"],
                "empty=",
                features["empty_cells"],
                "mean_domain=",
                round(features["mean_domain_size"], 3),
                "entropy=",
                round(features["candidate_domain_entropy"], 3),
            )

    fieldnames = [
        "puzzle_id",
        "clue_count",
        "empty_cells",
        "mean_domain_size",
        "domain_variance",
        "min_domain_size",
        "max_domain_size",
        "singleton_count",
        "singleton_ratio",
        "pair_count",
        "pair_ratio",
        "triple_count",
        "triple_ratio",
        "candidate_domain_entropy",
    ]

    with OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("Structural features written to:")
    print(OUTPUT)


if __name__ == "__main__":
    main()
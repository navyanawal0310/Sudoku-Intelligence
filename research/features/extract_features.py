import csv
from pathlib import Path

from candidate_features import extract_candidate_features
from propagation_features import propagate_naked_singles


INPUT = Path(
    "research/data/pilot/puzzles_100.csv"
)

OUTPUT = Path(
    "research/results/structural_features_100.csv"
)


def main():

    rows = []

    with INPUT.open(
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for record in reader:

            # -----------------------------
            # Layer 1: Static structure
            # -----------------------------
            features = extract_candidate_features(
                record["puzzle"]
            )

            # -----------------------------
            # Layer 2: Propagation response
            # -----------------------------
            propagation = propagate_naked_singles(
                record["puzzle"]
            )

            features.update(propagation)

            features["puzzle_id"] = (
                record["puzzle_id"]
            )

            rows.append(features)

            print(
                record["puzzle_id"],
                "empty=",
                features["empty_cells"],
                "mean_domain=",
                round(
                    features["mean_domain_size"],
                    3
                ),
                "entropy=",
                round(
                    features[
                        "candidate_domain_entropy"
                    ],
                    3
                ),
                "forced=",
                features[
                    "prop_forced_assignments"
                ],
                "rounds=",
                features["prop_rounds"],
                "residual=",
                features[
                    "prop_residual_empty"
                ],
            )

    fieldnames = [
        # Identity
        "puzzle_id",

        # Static density
        "clue_count",
        "empty_cells",

        # Candidate-domain structure
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

        # Spatial structure
        "row_clue_variance",
        "column_clue_variance",
        "box_clue_variance",

        "min_row_clues",
        "max_row_clues",

        "min_column_clues",
        "max_column_clues",

        "min_box_clues",
        "max_box_clues",

        # Propagation-response signature
        "prop_initial_empty",
        "prop_initial_singletons",
        "prop_forced_assignments",
        "prop_rounds",
        "prop_reduction_ratio",
        "prop_residual_empty",
        "prop_initial_mean_domain",
        "prop_final_mean_domain",
        "prop_final_singletons",
        "prop_contradiction",
        "prop_solved",
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
    print("Structural + propagation features written to:")
    print(OUTPUT)
    print("Rows:", len(rows))


if __name__ == "__main__":
    main()
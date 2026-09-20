import csv
import math
import random
from pathlib import Path


INPUT = Path(
    "research/results/analysis_dataset_100.csv"
)

SEED = 2026
FOLDS = 5


BASELINE_FEATURES = [
    "empty_cells",
]


STATIC_FEATURES = [
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


PROPAGATION_FEATURES = [
    "prop_forced_assignments",
    "prop_rounds",
    "prop_reduction_ratio",
    "prop_residual_empty",
    "prop_final_mean_domain",
]


def load_data():

    with INPUT.open(
        newline="",
        encoding="utf-8"
    ) as file:

        return list(csv.DictReader(file))


def extract_matrix(rows, features):

    X = []

    for row in rows:

        X.append([
            float(row[feature])
            for feature in features
        ])

    return X


def extract_target(rows):

    return [
        float(row["log_recursive_calls"])
        for row in rows
    ]


def mean(values):
    return sum(values) / len(values)


def standardize_train_test(
    X_train,
    X_test
):
    """
    Standardize using training-set statistics only.
    Prevents validation leakage.
    """

    columns = len(X_train[0])

    means = []
    stds = []

    for j in range(columns):

        values = [
            row[j]
            for row in X_train
        ]

        mu = mean(values)

        variance = mean([
            (value - mu) ** 2
            for value in values
        ])

        sigma = math.sqrt(variance)

        if sigma == 0:
            sigma = 1.0

        means.append(mu)
        stds.append(sigma)

    def transform(X):

        result = []

        for row in X:

            result.append([
                (row[j] - means[j])
                / stds[j]
                for j in range(columns)
            ])

        return result

    return (
        transform(X_train),
        transform(X_test),
    )


def solve_linear_system(A, b):
    """
    Gaussian elimination.

    Used to fit ordinary least squares without
    requiring an external ML package.
    """

    n = len(A)

    matrix = [
        A[i][:] + [b[i]]
        for i in range(n)
    ]

    for i in range(n):

        pivot = max(
            range(i, n),
            key=lambda r: abs(matrix[r][i])
        )

        matrix[i], matrix[pivot] = (
            matrix[pivot],
            matrix[i]
        )

        if abs(matrix[i][i]) < 1e-12:
            matrix[i][i] += 1e-8

        divisor = matrix[i][i]

        for j in range(i, n + 1):
            matrix[i][j] /= divisor

        for r in range(n):

            if r == i:
                continue

            factor = matrix[r][i]

            for j in range(i, n + 1):
                matrix[r][j] -= (
                    factor * matrix[i][j]
                )

    return [
        matrix[i][n]
        for i in range(n)
    ]


def fit_linear_regression(X, y):

    # Add intercept.
    X_design = [
        [1.0] + row
        for row in X
    ]

    columns = len(X_design[0])

    xtx = [
        [0.0] * columns
        for _ in range(columns)
    ]

    xty = [0.0] * columns

    for row, target in zip(
        X_design,
        y
    ):

        for i in range(columns):

            xty[i] += row[i] * target

            for j in range(columns):

                xtx[i][j] += (
                    row[i] * row[j]
                )

    # Tiny ridge term for numerical stability.
    # Do not regularize intercept.
    for i in range(1, columns):
        xtx[i][i] += 1e-8

    return solve_linear_system(
        xtx,
        xty
    )


def predict(X, coefficients):

    predictions = []

    for row in X:

        value = coefficients[0]

        for coefficient, feature in zip(
            coefficients[1:],
            row
        ):
            value += coefficient * feature

        predictions.append(value)

    return predictions


def rmse(actual, predicted):

    return math.sqrt(
        mean([
            (a - p) ** 2
            for a, p in zip(
                actual,
                predicted
            )
        ])
    )


def mae(actual, predicted):

    return mean([
        abs(a - p)
        for a, p in zip(
            actual,
            predicted
        )
    ])


def r_squared(actual, predicted):

    baseline = mean(actual)

    ss_total = sum(
        (value - baseline) ** 2
        for value in actual
    )

    ss_residual = sum(
        (a - p) ** 2
        for a, p in zip(
            actual,
            predicted
        )
    )

    if ss_total == 0:
        return 0.0

    return 1 - (
        ss_residual / ss_total
    )


def make_folds(n):

    indices = list(range(n))

    rng = random.Random(SEED)
    rng.shuffle(indices)

    folds = [
        []
        for _ in range(FOLDS)
    ]

    for position, index in enumerate(indices):

        folds[position % FOLDS].append(
            index
        )

    return folds


def cross_validate(
    rows,
    features
):

    X = extract_matrix(
        rows,
        features
    )

    y = extract_target(rows)

    folds = make_folds(len(rows))

    all_actual = []
    all_predictions = []

    for fold_number in range(FOLDS):

        test_indices = set(
            folds[fold_number]
        )

        X_train = [
            X[i]
            for i in range(len(X))
            if i not in test_indices
        ]

        y_train = [
            y[i]
            for i in range(len(y))
            if i not in test_indices
        ]

        X_test = [
            X[i]
            for i in range(len(X))
            if i in test_indices
        ]

        y_test = [
            y[i]
            for i in range(len(y))
            if i in test_indices
        ]

        (
            X_train_scaled,
            X_test_scaled,
        ) = standardize_train_test(
            X_train,
            X_test
        )

        coefficients = fit_linear_regression(
            X_train_scaled,
            y_train
        )

        predictions = predict(
            X_test_scaled,
            coefficients
        )

        all_actual.extend(y_test)
        all_predictions.extend(predictions)

    return {
        "r2": r_squared(
            all_actual,
            all_predictions
        ),

        "rmse": rmse(
            all_actual,
            all_predictions
        ),

        "mae": mae(
            all_actual,
            all_predictions
        ),
    }


def main():

    rows = load_data()

    models = [
        (
            "M0 Density",
            BASELINE_FEATURES
        ),

        (
            "M1 Static",
            STATIC_FEATURES
        ),

        (
            "M2 Static + Propagation",
            STATIC_FEATURES
            + PROPAGATION_FEATURES
        ),
    ]

    print()
    print("Structural-Search Ablation")
    print("==========================")
    print(f"N       : {len(rows)}")
    print(f"CV folds: {FOLDS}")
    print(f"Seed    : {SEED}")

    print()
    print(
        f"{'Model':26s}"
        f"{'Features':>10s}"
        f"{'R2':>10s}"
        f"{'RMSE':>10s}"
        f"{'MAE':>10s}"
    )

    print("-" * 66)

    results = []

    for name, features in models:

        result = cross_validate(
            rows,
            features
        )

        results.append(
            (name, result)
        )

        print(
            f"{name:26s}"
            f"{len(features):10d}"
            f"{result['r2']:10.4f}"
            f"{result['rmse']:10.4f}"
            f"{result['mae']:10.4f}"
        )

    print()
    print("Incremental change")
    print("------------------")

    m0 = results[0][1]
    m1 = results[1][1]
    m2 = results[2][1]

    print(
        "M1 - M0 R2 :",
        round(
            m1["r2"] - m0["r2"],
            4
        )
    )

    print(
        "M2 - M1 R2 :",
        round(
            m2["r2"] - m1["r2"],
            4
        )
    )

    print(
        "M2 - M0 R2 :",
        round(
            m2["r2"] - m0["r2"],
            4
        )
    )


if __name__ == "__main__":
    main()
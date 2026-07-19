import os
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/output/results.csv"

df = pd.read_csv(INPUT_FILE)
features = [
    "recursive_calls",
    "backtracks",
    "candidate_checks",
    "maximum_depth"
]

target = "execution_time_ms"
for feature in features:

    plt.figure(figsize=(7,5))

    plt.scatter(
        df[feature],
        df[target]
    )

    plt.xlabel(feature)
    plt.ylabel(target)

    plt.title(f"{feature} vs {target}")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        f"images/{feature}_vs_execution.png",
        dpi=300
    )

    plt.close()

correlation = df.corr(numeric_only=True)

ranking = correlation[target].sort_values(
    ascending=False
)

with open("reports/regression_report.txt", "w") as report:

    report.write("REGRESSION ANALYSIS REPORT\n")
    report.write("=" * 50 + "\n\n")

    report.write("Correlation Ranking with Execution Time\n")
    report.write("-" * 50 + "\n\n")

    for feature, corr in ranking.items():
        report.write(f"{feature:<25} {corr:.4f}\n")

print("\nRegression report generated successfully!")
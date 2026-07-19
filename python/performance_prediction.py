import os
import pandas as pd
import matplotlib.pyplot as plt
from interpolation import newton_divided_interpolation
# =====================================
# File Paths
# =====================================

INPUT_FILE = "data/output/results.csv"
OUTPUT_FILE = "data/output/grouped_results.csv"

IMAGE_DIR = "images"

os.makedirs(IMAGE_DIR, exist_ok=True)

# =====================================
# Load Dataset
# =====================================

df = pd.read_csv(INPUT_FILE)

print("Dataset Loaded Successfully")
print(f"Total Records : {len(df)}")

# =====================================
# Keep Required Columns
# =====================================

df = df[
    [
        "empty_cells",
        "recursive_calls",
        "backtracks",
        "execution_time_ms",
    ]
]

# =====================================
# Sort by Difficulty
# =====================================

df = df.sort_values("empty_cells")

# =====================================
# Group by Difficulty
# =====================================

grouped = (
    df.groupby("empty_cells")
      .agg(
          {
              "recursive_calls": "mean",
              "backtracks": "mean",
              "execution_time_ms": "mean",
          }
      )
      .reset_index()
)
# =====================================
# Prepare Data for Interpolation
# =====================================
x = grouped["empty_cells"].tolist()
recursive = grouped["recursive_calls"].tolist()
backtracks = grouped["backtracks"].tolist()
execution = grouped["execution_time_ms"].tolist()

# =====================================
# Save Grouped Dataset
# =====================================

grouped.to_csv(OUTPUT_FILE, index=False)

print("\nGrouped dataset created successfully!")
print(grouped.head())

# =====================================
# Plot 1
# Recursive Calls
# =====================================

plt.figure(figsize=(8,5))

plt.plot(
    grouped["empty_cells"],
    grouped["recursive_calls"],
    marker="o"
)

plt.title("Recursive Calls vs Empty Cells")
plt.xlabel("Empty Cells")
plt.ylabel("Average Recursive Calls")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "images/recursive_prediction_curve.png",
    dpi=300
)

plt.close()

# =====================================
# Plot 2
# Backtracks
# =====================================

plt.figure(figsize=(8,5))

plt.plot(
    grouped["empty_cells"],
    grouped["backtracks"],
    marker="o"
)

plt.title("Backtracks vs Empty Cells")
plt.xlabel("Empty Cells")
plt.ylabel("Average Backtracks")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "images/backtracks_prediction_curve.png",
    dpi=300
)

plt.close()

# =====================================
# Plot 3
# Execution Time
# =====================================

plt.figure(figsize=(8,5))

plt.plot(
    grouped["empty_cells"],
    grouped["execution_time_ms"],
    marker="o"
)

plt.title("Execution Time vs Empty Cells")
plt.xlabel("Empty Cells")
plt.ylabel("Average Execution Time (ms)")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "images/execution_time_prediction_curve.png",
    dpi=300
)

plt.close()

print("\nPrediction dataset and graphs generated successfully!")
print("==============================")
print("NEWTON DIVIDED DIFFERENCE")
print("==============================")

value = float(input("Enter Empty Cells: "))

recursive_prediction = newton_divided_interpolation(
    x,
    recursive,
    value
)

backtrack_prediction = newton_divided_interpolation(
    x,
    backtracks,
    value
)

execution_prediction = newton_divided_interpolation(
    x,
    execution,
    value
)

print("\nPrediction Results")
print("-" * 40)
print(f"Empty Cells                 : {value}")
print(f"Recursive Calls             : {recursive_prediction:.2f}")
print(f"Backtracks                  : {backtrack_prediction:.2f}")
print(f"Execution Time (ms)         : {execution_prediction:.4f}")

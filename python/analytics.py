import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Load Dataset
# ----------------------------
df = pd.read_csv("data/output/results.csv")
print(df.columns.tolist())
print(df)

print("\n========== SUMMARY ==========\n")

print(f"Total Puzzles           : {len(df)}")
print(f"Average Recursive Calls : {df['recursive_calls'].mean():.2f}")
print(f"Average Backtracks      : {df['backtracks'].mean():.2f}")
print(f"Average Time            : {df['execution_time_ms'].mean():.6f} sec")

print("\nHardest Puzzle")
print(df.loc[df["recursive_calls"].idxmax()])

print("\nEasiest Puzzle")
print(df.loc[df["recursive_calls"].idxmin()])

plt.figure(figsize=(8,5))

plt.bar(df["id"], df["recursive_calls"])

plt.title("Recursive Calls per Puzzle")
plt.xlabel("Puzzle ID")
plt.ylabel("Recursive Calls")

plt.tight_layout()

plt.savefig("../images/recursive_calls.png", dpi=300)

plt.close()

plt.figure(figsize=(8,5))

plt.bar(df["id"], df["backtracks"])

plt.title("Backtracks per Puzzle")
plt.xlabel("Puzzle ID")
plt.ylabel("Backtracks")

plt.tight_layout()

plt.savefig("../images/backtracks.png", dpi=300)

plt.close()

plt.figure(figsize=(8,5))

plt.bar(df["id"], df["execution_time_ms"])

plt.title("Execution Time per Puzzle")
plt.xlabel("Puzzle ID")
plt.ylabel("Execution Time (seconds)")

plt.tight_layout()

plt.savefig("../images/execution_time.png", dpi=300)

plt.close()

plt.figure(figsize=(8,5))

plt.hist(df["recursive_calls"], bins=10)

plt.title("Distribution of Recursive Calls")
plt.xlabel("Recursive Calls")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig("../images/recursive_histogram.png", dpi=300)

plt.close()

plt.figure(figsize=(8,5))

plt.scatter(df["recursive_calls"],
            df["execution_time_ms"])

plt.title("Recursive Calls vs Execution Time")
plt.xlabel("Recursive Calls")
plt.ylabel("Execution Time")

plt.tight_layout()

plt.savefig("../images/correlation.png", dpi=300)

plt.close()

with open("../reports/analysis_report.txt","w") as report:

    report.write("Sudoku Intelligence Lab\n")
    report.write("=======================\n\n")

    report.write(f"Total puzzles: {len(df)}\n")
    report.write(f"Average recursive calls: {df['recursive_calls'].mean():.2f}\n")
    report.write(f"Average backtracks: {df['backtracks'].mean():.2f}\n")
    report.write(f"Average execution time: {df['execution_time_ms'].mean():.6f} sec\n\n")

    report.write("Hardest Puzzle\n")
    report.write(df.loc[df["recursive_calls"].idxmax()].to_string())

    report.write("\n\nEasiest Puzzle\n")
    report.write(df.loc[df["recursive_calls"].idxmin()].to_string())
import os
import math
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/output/results.csv"

os.makedirs("reports", exist_ok=True)
os.makedirs("images", exist_ok=True)

df = pd.read_csv(INPUT_FILE)
x = df["recursive_calls"].tolist()
y = df["execution_time_ms"].tolist()
def linear_regression(x, y):

    n = len(x)

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = 0
    denominator = 0

    for xi, yi in zip(x, y):

        numerator += (xi - mean_x) * (yi - mean_y)
        denominator += (xi - mean_x) ** 2

    slope = numerator / denominator
    intercept = mean_y - slope * mean_x

    return slope, intercept

def predict(x, slope, intercept):

    predictions = []

    for value in x:
        predictions.append(intercept + slope * value)

    return predictions

def evaluate(actual, predicted):

    n = len(actual)

    mae = 0
    mse = 0

    mean_actual = sum(actual) / n

    ss_total = 0
    ss_residual = 0

    for a, p in zip(actual, predicted):

        error = a - p

        mae += abs(error)
        mse += error ** 2

        ss_total += (a - mean_actual) ** 2
        ss_residual += error ** 2

    mae /= n
    rmse = math.sqrt(mse / n)
    r2 = 1 - (ss_residual / ss_total)
    return mae, rmse, r2

slope, intercept = linear_regression(x, y)
predicted = predict(x, slope, intercept)
mae, rmse, r2 = evaluate(y, predicted)
print("\nLINEAR REGRESSION RESULTS")
print("=" * 40)

print(f"Slope      : {slope:.8f}")
print(f"Intercept  : {intercept:.8f}")

print(f"MAE        : {mae:.4f}")
print(f"RMSE       : {rmse:.4f}")
print(f"R²         : {r2:.4f}")
plt.figure(figsize=(8,6))
combined = sorted(zip(x, predicted))

sorted_x = [p[0] for p in combined]
sorted_predicted = [p[1] for p in combined]

plt.figure(figsize=(8,6))

plt.scatter(x, y, alpha=0.5)

plt.plot(
    sorted_x,
    sorted_predicted,
    linewidth=2,
    color="red"
)

plt.xlabel("Recursive Calls")
plt.ylabel("Execution Time (ms)")
plt.title("Linear Regression")

plt.grid(True)
plt.tight_layout()

plt.savefig("images/linear_regression.png", dpi=300)
plt.close()

REPORT_FILE = "reports/linear_regression_report.txt"

with open(REPORT_FILE, "w") as report:

    report.write("LINEAR REGRESSION REPORT\n")
    report.write("=" * 50 + "\n\n")

    report.write(f"Slope      : {slope:.8f}\n")
    report.write(f"Intercept  : {intercept:.8f}\n\n")

    report.write("MODEL PERFORMANCE\n")
    report.write("-" * 30 + "\n")

    report.write(f"MAE        : {mae:.4f}\n")
    report.write(f"RMSE       : {rmse:.4f}\n")
    report.write(f"R²         : {r2:.4f}\n\n")

    report.write("INTERPRETATION\n")
    report.write("-" * 30 + "\n")

    if r2 >= 0.95:
        report.write("Excellent fit. Recursive calls are a very strong predictor of execution time.\n")
    elif r2 >= 0.80:
        report.write("Good fit. The model explains most of the variation in execution time.\n")
    else:
        report.write("Weak fit. Additional features may be required.\n")

print(f"\nReport saved to: {REPORT_FILE}")
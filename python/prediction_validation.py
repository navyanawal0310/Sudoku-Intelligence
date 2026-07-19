import math
import os

import matplotlib.pyplot as plt
import pandas as pd

from interpolation import newton_divided_interpolation

INPUT_FILE = "data/output/grouped_results.csv"

REPORT_FILE = "reports/validation_report.txt"

os.makedirs("reports", exist_ok=True)
os.makedirs("images", exist_ok=True)

df = pd.read_csv(INPUT_FILE)

x = df["empty_cells"].tolist()
y = df["recursive_calls"].tolist()

def leave_one_out_validation(x, y):

    actual = []
    predicted = []

    for i in range(len(x)):

        x_train = x[:i] + x[i + 1:]
        y_train = y[:i] + y[i + 1:]

        x_test = x[i]

        prediction = newton_divided_interpolation(
            x_train,
            y_train,
            x_test
        )

        actual.append(y[i])
        predicted.append(prediction)

    return actual, predicted

def calculate_metrics(actual, predicted):

    n = len(actual)

    mae = 0
    mse = 0
    mape = 0

    mean_actual = sum(actual) / n

    ss_total = 0
    ss_residual = 0

    for a, p in zip(actual, predicted):

        error = a - p

        mae += abs(error)

        mse += error ** 2

        if a != 0:
            mape += abs(error) / abs(a)

        ss_total += (a - mean_actual) ** 2
        ss_residual += error ** 2

    mae /= n

    rmse = math.sqrt(mse / n)

    mape = (mape / n) * 100

    r2 = 1 - (ss_residual / ss_total)

    return mae, rmse, mape, r2

actual, predicted = leave_one_out_validation(x, y)

mae, rmse, mape, r2 = calculate_metrics(actual, predicted)

with open(REPORT_FILE, "w") as report:
    report.write("PREDICTION VALIDATION REPORT\n")
    report.write("=" * 40 + "\n\n")
    report.write(f"MAE   : {mae:.4f}\n")
    report.write(f"RMSE  : {rmse:.4f}\n")
    report.write(f"MAPE  : {mape:.2f}%\n")
    report.write(f"R²    : {r2:.4f}\n")
plt.figure(figsize=(7,7))
plt.scatter(actual, predicted)
minimum = min(actual)
maximum = max(actual)
plt.plot(
    [minimum, maximum],
    [minimum, maximum],
    linestyle="--"
)
plt.xlabel("Actual")
plt.ylabel("Predicted")
plt.title("Actual vs Predicted Recursive Calls")
plt.grid(True)
plt.tight_layout()
plt.savefig(
    "images/validation_plot.png",
    dpi=300
)
plt.close()
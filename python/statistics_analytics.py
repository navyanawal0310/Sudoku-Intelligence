import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# File Paths
# ==========================

INPUT_FILE = "data/output/results.csv"
REPORT_FILE = "reports/statistics_report.txt"

IMAGE_DIR = "images"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs("reports", exist_ok=True)

# ==========================
# Load Dataset
# ==========================

df = pd.read_csv(INPUT_FILE)

print("Dataset Loaded Successfully")
print(df.head())

# ==========================
# Dataset Information
# ==========================

rows, cols = df.shape

missing_values = df.isnull().sum().sum()

duplicate_rows = df.duplicated().sum()

# ==========================
# Numerical Columns
# ==========================

metrics = [
    "empty_cells",
    "recursive_calls",
    "backtracks",
    "candidate_checks",
    "successful_assignments",
    "failed_assignments",
    "maximum_depth",
    "execution_time_ms"
]

# ==========================
# Write Report
# ==========================

with open(REPORT_FILE, "w") as report:

    report.write("STATISTICAL ANALYSIS REPORT\n")
    report.write("=" * 50 + "\n\n")

    report.write("DATASET SUMMARY\n")
    report.write("-" * 30 + "\n")

    report.write(f"Rows              : {rows}\n")
    report.write(f"Columns           : {cols}\n")
    report.write(f"Missing Values    : {missing_values}\n")
    report.write(f"Duplicate Rows    : {duplicate_rows}\n\n")

    report.write("DESCRIPTIVE STATISTICS\n")
    report.write("-" * 30 + "\n\n")

    for column in metrics:

        report.write(f"{column.upper()}\n")

        report.write(f"Count      : {df[column].count()}\n")
        report.write(f"Mean       : {df[column].mean():.4f}\n")
        report.write(f"Median     : {df[column].median():.4f}\n")

        mode = df[column].mode()

        if len(mode) > 0:
            report.write(f"Mode       : {mode.iloc[0]}\n")

        report.write(f"Minimum    : {df[column].min()}\n")
        report.write(f"Maximum    : {df[column].max()}\n")
        report.write(f"Range      : {df[column].max() - df[column].min()}\n")

        report.write(f"Variance   : {df[column].var():.4f}\n")
        report.write(f"Std Dev    : {df[column].std():.4f}\n")

        report.write(f"Q1         : {df[column].quantile(0.25):.4f}\n")
        report.write(f"Q3         : {df[column].quantile(0.75):.4f}\n")

        iqr = (
            df[column].quantile(0.75)
            - df[column].quantile(0.25)
        )

        report.write(f"IQR        : {iqr:.4f}\n")

        report.write(f"Skewness   : {df[column].skew():.4f}\n")
        report.write(f"Kurtosis   : {df[column].kurt():.4f}\n")

        report.write("\n")
#correlation matrix
correlation = df[metrics].corr(method="pearson")
plt.figure(figsize=(10,8))
plt.imshow(correlation, interpolation="nearest")
plt.colorbar()
plt.xticks(range(len(metrics)), metrics, rotation=45, ha="right")
plt.yticks(range(len(metrics)), metrics)
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig("images/correlation_heatmap.png", dpi=300)
plt.close()
#histogram
for column in metrics:
    plt.figure(figsize=(7,5))
    plt.hist(df[column], bins=20)
    plt.title(f"{column} Distribution")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"images/{column}_histogram.png", dpi=300)
    plt.close()
#boxplots
for column in metrics:
    plt.figure(figsize=(6,4))
    plt.boxplot(df[column], vert=True)
    plt.title(f"{column} Boxplot")
    plt.tight_layout()
    plt.savefig(f"images/{column}_boxplot.png", dpi=300)
    plt.close()

#outlier detection
report.write("\n")
report.write("="*50 + "\n")
report.write("OUTLIER ANALYSIS\n")
report.write("="*50 + "\n\n")
for column in metrics:
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[
        (df[column] < lower) |
        (df[column] > upper)
    ]
    report.write(f"{column}\n")
    report.write(f"Outliers : {len(outliers)}\n\n")


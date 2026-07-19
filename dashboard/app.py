import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------
# Page Config
# -----------------------

st.set_page_config(
    page_title="Sudoku Intelligence Lab",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        div[data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 10px;
            padding: 12px 16px;
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
        }
        .block-container {
            padding-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧩 Sudoku Intelligence Lab")
st.caption("Performance Analysis of a Recursive Backtracking Sudoku Solver")

# -----------------------
# Load Data
# -----------------------

DATA_PATH = "data/output/results.csv"

REQUIRED_COLUMNS = [
    "id",
    "empty_cells",
    "recursive_calls",
    "backtracks",
    "candidate_checks",
    "successful_assignments",
    "failed_assignments",
    "maximum_depth",
    "execution_time_ms",
    "solved",
]

DIFFICULTY_ORDER = ["Easy", "Medium", "Hard", "Expert"]
DIFFICULTY_BUCKET_SIZE = 250


@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path)
    except FileNotFoundError:
        return None
    return data


def derive_difficulty(row_id):
    """Map a puzzle id to a difficulty label based on generation order
    (250 Easy, 250 Medium, 250 Hard, 250 Expert)."""
    index = int(row_id) - 1
    bucket = index // DIFFICULTY_BUCKET_SIZE
    bucket = min(bucket, len(DIFFICULTY_ORDER) - 1)
    return DIFFICULTY_ORDER[bucket]


df = load_data(DATA_PATH)

# -----------------------
# Empty / Missing Dataset Handling
# -----------------------

if df is None:
    st.error(f"Could not find results file at `{DATA_PATH}`. Run the benchmark first.")
    st.stop()

if df.empty:
    st.warning("The results dataset is empty. Run the benchmark to generate data.")
    st.stop()

missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing_columns:
    st.error(f"Dataset is missing expected columns: {', '.join(missing_columns)}")
    st.stop()

if "difficulty" not in df.columns:
    df["difficulty"] = df["id"].apply(derive_difficulty)

# -----------------------
# Sidebar Filters
# -----------------------

st.sidebar.header("Filters")

available_difficulties = [d for d in DIFFICULTY_ORDER if d in df["difficulty"].unique()]
selected_difficulties = st.sidebar.multiselect(
    "Difficulty",
    options=available_difficulties,
    default=available_difficulties,
)

solved_options = sorted(df["solved"].unique().tolist())
selected_solved = st.sidebar.multiselect(
    "Solved Status",
    options=solved_options,
    default=solved_options,
    format_func=lambda v: "Solved" if v == 1 else "Unsolved",
)

id_min, id_max = int(df["id"].min()), int(df["id"].max())
id_range = st.sidebar.slider(
    "Puzzle ID Range",
    min_value=id_min,
    max_value=id_max,
    value=(id_min, id_max),
)

filtered_df = df[
    df["difficulty"].isin(selected_difficulties)
    & df["solved"].isin(selected_solved)
    & df["id"].between(id_range[0], id_range[1])
]

st.sidebar.markdown(f"**{len(filtered_df)}** of **{len(df)}** puzzles selected")

# -----------------------
# Empty Filtered Dataset Handling
# -----------------------

if filtered_df.empty:
    st.info("No puzzles match the current filters. Adjust the filters in the sidebar.")
    st.stop()

# -----------------------
# KPI Cards
# -----------------------

solve_rate = filtered_df["solved"].mean() * 100

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Total Puzzles", len(filtered_df))
kpi2.metric("Avg Recursive Calls", f"{filtered_df['recursive_calls'].mean():,.0f}")
kpi3.metric("Avg Backtracks", f"{filtered_df['backtracks'].mean():,.0f}")
kpi4.metric("Avg Execution Time", f"{filtered_df['execution_time_ms'].mean():.3f} ms")
kpi5.metric("Solve Rate", f"{solve_rate:.1f}%")

st.divider()

# -----------------------
# Interactive Charts: Metrics by Puzzle
# -----------------------

st.subheader("Solver Metrics by Puzzle")

tab1, tab2, tab3 = st.tabs(["Recursive Calls", "Backtracks", "Execution Time"])

with tab1:
    fig = px.bar(
        filtered_df,
        x="id",
        y="recursive_calls",
        color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        labels={"id": "Puzzle ID", "recursive_calls": "Recursive Calls"},
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.bar(
        filtered_df,
        x="id",
        y="backtracks",
        color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        labels={"id": "Puzzle ID", "backtracks": "Backtracks"},
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.bar(
        filtered_df,
        x="id",
        y="execution_time_ms",
        color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        labels={"id": "Puzzle ID", "execution_time_ms": "Execution Time (ms)"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------
# Difficulty Distribution
# -----------------------

st.subheader("Distribution by Difficulty")

dist_col1, dist_col2 = st.columns(2)

with dist_col1:
    fig = px.box(
        filtered_df,
        x="difficulty",
        y="recursive_calls",
        color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        labels={"difficulty": "Difficulty", "recursive_calls": "Recursive Calls"},
        title="Recursive Calls by Difficulty",
    )
    st.plotly_chart(fig, use_container_width=True)

with dist_col2:
    fig = px.box(
        filtered_df,
        x="difficulty",
        y="execution_time_ms",
        color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        labels={"difficulty": "Difficulty", "execution_time_ms": "Execution Time (ms)"},
        title="Execution Time by Difficulty",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------
# Correlation Analysis
# -----------------------

st.subheader("Correlation Between Metrics")

numeric_columns = [
    "empty_cells",
    "recursive_calls",
    "backtracks",
    "candidate_checks",
    "successful_assignments",
    "failed_assignments",
    "maximum_depth",
    "execution_time_ms",
]
numeric_columns = [c for c in numeric_columns if c in filtered_df.columns]

corr_col1, corr_col2 = st.columns([1, 1])

with corr_col1:
    if len(filtered_df) > 1 and len(numeric_columns) > 1:
        corr_matrix = filtered_df[numeric_columns].corr()
        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Metric Correlation Heatmap",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to compute correlations.")

with corr_col2:
    fig = px.scatter(
        filtered_df,
        x="empty_cells",
        y="recursive_calls",
        color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        trendline="ols" if len(filtered_df) > 1 else None,
        labels={"empty_cells": "Empty Cells", "recursive_calls": "Recursive Calls"},
        title="Empty Cells vs. Recursive Calls",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------
# Hardest and Easiest Puzzle
# -----------------------

st.subheader("Hardest and Easiest Puzzle")

hard_col, easy_col = st.columns(2)

hardest = filtered_df.loc[[filtered_df["recursive_calls"].idxmax()]]
easiest = filtered_df.loc[[filtered_df["recursive_calls"].idxmin()]]

with hard_col:
    st.markdown("**Hardest Puzzle** (most recursive calls)")
    st.dataframe(hardest, use_container_width=True)

with easy_col:
    st.markdown("**Easiest Puzzle** (fewest recursive calls)")
    st.dataframe(easiest, use_container_width=True)

st.divider()

# -----------------------
# Dataset Table
# -----------------------

st.subheader("Dataset")
st.dataframe(filtered_df, use_container_width=True)

st.download_button(
    "Download filtered dataset as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_sudoku_results.csv",
    mime="text/csv",
)
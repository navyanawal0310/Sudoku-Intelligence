"""
Sudoku Intelligence Lab — multi-page Streamlit dashboard.

This app renders puzzles using the project's own `sudoku_renderer.py` and
`puzzle_utils.py` when they expose a recognizable function (any of a few
common names are tried). If those modules are missing, or don't expose a
usable function, the app falls back to a small built-in Plotly board
renderer and a lightweight backtracking solver, so the dashboard always
runs. The fallback solver is only used to visualize a solution in the
Explorer page — it is not the instrumented C solver used for benchmarking.
"""

import importlib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# Theme
# =========================================================

ACCENT = "#69BD5E"
BG = "#0A0A0C"
BG_PANEL = "#0E0F11"
BG_CARD = "#131316"
BORDER = "rgba(255,255,255,0.08)"
TEXT = "#E4E4E7"
TEXT_MUTED = "#8B8D98"

DIFFICULTY_ORDER = ["Easy", "Medium", "Hard", "Expert"]
DIFFICULTY_BUCKET_SIZE = 250
DIFFICULTY_COLORS = {
    "Easy": "#69BD5E",
    "Medium": "#3FA7D6",
    "Hard": "#F2B134",
    "Expert": "#E85D5D",
}

RESULTS_PATH = "data/output/results.csv"
PUZZLES_PATH = "data/dataset/sudoku_dataset.csv"

REQUIRED_RESULT_COLUMNS = [
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

NUMERIC_METRICS = [
    "empty_cells",
    "recursive_calls",
    "backtracks",
    "candidate_checks",
    "successful_assignments",
    "failed_assignments",
    "maximum_depth",
    "execution_time_ms",
]

DEMO_PUZZLE = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

PAGES = [
    "Home",
    "Explorer",
    "Performance",
    "Statistics",
    "Regression",
    "Prediction",
    "Research",
    "About",
]

ANALYTICS_PAGES = {
    "Performance",
    "Statistics",
    "Regression",
    "Prediction",
    "Research",
}

# =========================================================
# Optional project modules (rendered / solved via user's own code)
# =========================================================


def _try_import(module_name):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


sudoku_renderer = _try_import("sudoku_renderer")
puzzle_utils = _try_import("puzzle_utils")

HAVE_RENDERER = sudoku_renderer is not None
HAVE_PUZZLE_UTILS = puzzle_utils is not None


# =========================================================
# Page config + global styling
# =========================================================


def configure_page():
    st.set_page_config(
        page_title="Sudoku Intelligence Lab",
        page_icon="S",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.markdown(
        f"""
        <style>
            header[data-testid="stHeader"] {{
            background-color: transparent;
            height: 0;
        }}

            div[data-testid="stToolbar"] {{
                display: none;
            }}

            div[data-testid="stDecoration"] {{
                display: none;
            }}

            .block-container {{
                padding-top: 1rem;
            }}
            html, body, .stApp {{
                background-color: {BG};
                color: {TEXT};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                    Helvetica, Arial, sans-serif;
            }}
            section[data-testid="stSidebar"] {{
                background-color: {BG_PANEL};
                border-right: 1px solid {BORDER};
            }}
            h1, h2, h3, h4 {{
                color: {TEXT};
                font-weight: 600;
                letter-spacing: -0.01em;
            }}
            h1 {{
                font-size: 1.6rem;
                border-bottom: 1px solid {BORDER};
                padding-bottom: 0.6rem;
                margin-bottom: 0.4rem;
            }}
            h2, h3 {{
                font-size: 1.05rem;
            }}
            p, li, label, span {{
                color: {TEXT};
            }}
            .stCaption, [data-testid="stCaptionContainer"] {{
                color: {TEXT_MUTED} !important;
            }}

            /* KPI metric cards — green is used only for the left border */
            div[data-testid="stMetric"] {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 3px solid {ACCENT};
                border-radius: 8px;
                padding: 16px 18px;
            }}
            div[data-testid="stMetricLabel"] {{
                font-weight: 500;
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                color: {TEXT_MUTED};
            }}
            div[data-testid="stMetricValue"] {{
                color: {TEXT};
                font-weight: 600;
            }}

            /* Tabs — neutral, no color fill */
            .stTabs [data-baseweb="tab"] {{
                color: {TEXT_MUTED};
                font-weight: 500;
            }}
            .stTabs [aria-selected="true"] {{
                color: {TEXT} !important;
                border-bottom-color: {TEXT} !important;
            }}

            /* Buttons — neutral outline, no fill */
            .stButton>button, .stDownloadButton>button {{
                background-color: transparent;
                color: {TEXT};
                border: 1px solid {BORDER};
                font-weight: 500;
                border-radius: 6px;
            }}
            .stButton>button:hover, .stDownloadButton>button:hover {{
                border-color: rgba(255,255,255,0.2);
                background-color: rgba(255,255,255,0.03);
                color: {TEXT};
            }}

            .block-container {{
                padding-top: 2rem;
                max-width: 1280px;
            }}

            /* Plain content cards — title + description only */
            .sil-card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 20px 22px;
                height: 100%;
            }}
            .sil-card h4 {{
                color: {TEXT};
                font-size: 0.95rem;
                font-weight: 600;
                margin: 0 0 6px 0;
            }}
            .sil-card p {{
                color: {TEXT_MUTED};
                font-size: 0.85rem;
                line-height: 1.5;
                margin: 0;
            }}

            .sil-meta {{
                color: {TEXT_MUTED};
                font-size: 0.85rem;
                margin-top: -0.4rem;
                margin-bottom: 1.4rem;
            }}

            .sil-nav-label {{
                color: {TEXT_MUTED};
                font-size: 0.7rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin: 4px 0 6px 4px;
            }}

            /* Capabilities — hairline spec grid, typography only */
            .sil-spec-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                border-top: 1px solid {BORDER};
                border-left: 1px solid {BORDER};
            }}
            .sil-spec-cell {{
                padding: 20px 24px;
                border-right: 1px solid {BORDER};
                border-bottom: 1px solid {BORDER};
            }}
            .sil-spec-cell h4 {{
                margin: 0 0 6px 0;
                font-size: 0.92rem;
                font-weight: 600;
                color: {TEXT};
            }}
            .sil-spec-cell p {{
                margin: 0;
                font-size: 0.83rem;
                color: {TEXT_MUTED};
                line-height: 1.5;
            }}

            /* Key findings — elegant cards, green marks the edge only */
            .sil-finding {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 3px solid {ACCENT};
                border-radius: 6px;
                padding: 18px 20px;
                height: 100%;
            }}
            .sil-finding h4 {{
                margin: 0 0 6px 0;
                font-size: 0.88rem;
                font-weight: 600;
                color: {TEXT};
            }}
            .sil-finding p {{
                margin: 0;
                font-size: 0.82rem;
                color: {TEXT_MUTED};
                line-height: 1.5;
            }}

            .sil-section-label {{
                color: {TEXT_MUTED};
                font-size: 0.72rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin: 0 0 12px 2px;
            }}

            .sil-hero-panel {{
                border-left: 1px solid {BORDER};
                padding-left: 28px;
            }}

            /* Sidebar navigation — green marks only the active item */
            section[data-testid="stSidebar"] input[type="radio"] {{
                accent-color: {ACCENT};
            }}
            section[data-testid="stSidebar"] div[role="radiogroup"] label {{
                padding: 6px 10px;
                border-radius: 6px;
                border-left: 2px solid transparent;
                margin-bottom: 2px;
            }}
            section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
                background-color: rgba(255,255,255,0.04);
            }}
            section[data-testid="stSidebar"] div[role="radiogroup"] label p {{
                color: {TEXT_MUTED};
                font-size: 0.9rem;
                font-weight: 500;
            }}
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
                background-color: rgba(105,189,94,0.08);
                border-left: 2px solid {ACCENT};
            }}
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{
                color: {ACCENT};
                font-weight: 600;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Data loading
# =========================================================


@st.cache_data
def load_results(path):
    try:
        return pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None


@st.cache_data
def load_puzzles(path):
    try:
        return pd.read_csv(path, dtype={"puzzle": str})
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None


def derive_difficulty(row_id):
    """Map a puzzle id to a difficulty label based on generation order
    (250 Easy, 250 Medium, 250 Hard, 250 Expert)."""
    index = int(row_id) - 1
    bucket = max(index, 0) // DIFFICULTY_BUCKET_SIZE
    bucket = min(bucket, len(DIFFICULTY_ORDER) - 1)
    return DIFFICULTY_ORDER[bucket]


def prepare_results(df):
    if df is None or df.empty:
        return None
    missing = [c for c in REQUIRED_RESULT_COLUMNS if c not in df.columns]
    if missing:
        return None
    df = df.copy()
    if "difficulty" not in df.columns:
        df["difficulty"] = df["id"].apply(derive_difficulty)
    return df


# =========================================================
# Puzzle grid helpers (fallback implementations)
# =========================================================


def string_to_grid_fallback(puzzle_str):
    puzzle_str = "".join(ch for ch in str(puzzle_str) if ch.isdigit())
    puzzle_str = puzzle_str.ljust(81, "0")[:81]
    return [[int(puzzle_str[r * 9 + c]) for c in range(9)] for r in range(9)]


def _is_safe(grid, row, col, num):
    if num in grid[row]:
        return False
    if num in (grid[r][col] for r in range(9)):
        return False
    sr, sc = 3 * (row // 3), 3 * (col // 3)
    for r in range(sr, sr + 3):
        for c in range(sc, sc + 3):
            if grid[r][c] == num:
                return False
    return True


def solve_grid_fallback(grid):
    grid = [row[:] for row in grid]

    def backtrack():
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    for num in range(1, 10):
                        if _is_safe(grid, r, c, num):
                            grid[r][c] = num
                            if backtrack():
                                return True
                            grid[r][c] = 0
                    return False
        return True

    if backtrack():
        return grid
    return None


def get_grid_from_string(puzzle_str):
    if HAVE_PUZZLE_UTILS:
        for fn_name in ("parse_puzzle_string", "string_to_grid", "to_grid", "parse"):
            fn = getattr(puzzle_utils, fn_name, None)
            if callable(fn):
                try:
                    result = fn(puzzle_str)
                    if result:
                        return result
                except Exception:
                    pass
    return string_to_grid_fallback(puzzle_str)


def get_solution(grid, puzzle_str=None):
    if HAVE_PUZZLE_UTILS:
        for fn_name in ("solve_sudoku", "solve", "solve_puzzle"):
            fn = getattr(puzzle_utils, fn_name, None)
            if callable(fn):
                try:
                    arg = puzzle_str if puzzle_str is not None else [row[:] for row in grid]
                    result = fn(arg)
                    if result:
                        return result if isinstance(result[0], list) else get_grid_from_string(result)
                except Exception:
                    pass
    return solve_grid_fallback(grid)


def render_board_fallback(grid, title="", size=380):
    n = 9
    fig = go.Figure()
    font_size = max(12, int(size * 0.0526))

    for i in range(n + 1):
        thick = i % 3 == 0
        line = dict(color=ACCENT if thick else "rgba(228,228,231,0.18)", width=2.5 if thick else 1)
        fig.add_shape(type="line", x0=0, y0=i, x1=n, y1=i, line=line)
        fig.add_shape(type="line", x0=i, y0=0, x1=i, y1=n, line=line)

    for r in range(n):
        for c in range(n):
            val = grid[r][c]
            if val:
                fig.add_annotation(
                    x=c + 0.5,
                    y=n - r - 0.5,
                    text=str(val),
                    showarrow=False,
                    font=dict(size=font_size, color=TEXT),
                )

    fig.update_xaxes(visible=False, range=[0, n])
    fig.update_yaxes(visible=False, range=[0, n], scaleanchor="x")
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT_MUTED, size=14)),
        width=size,
        height=size,
        margin=dict(l=10, r=10, t=36, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def display_board(grid, title="", size=380):
    if HAVE_RENDERER:
        for fn_name in ("render_board", "render_sudoku", "draw_board", "render"):
            fn = getattr(sudoku_renderer, fn_name, None)
            if callable(fn):
                try:
                    result = fn(grid)
                except Exception:
                    result = None
                if result is not None:
                    if title:
                        st.markdown(f"**{title}**")
                    _render_unknown(result)
                    return
    st.plotly_chart(render_board_fallback(grid, title, size=size), use_container_width=False)


def _render_unknown(result):
    if hasattr(result, "to_plotly_json"):
        st.plotly_chart(result, use_container_width=False)
        return
    if hasattr(result, "savefig"):
        st.pyplot(result)
        return
    if isinstance(result, str):
        if result.strip().startswith("<"):
            st.markdown(result, unsafe_allow_html=True)
        else:
            st.text(result)
        return
    st.write(result)


# =========================================================
# Shared filtering + KPI helpers
# =========================================================


def render_sidebar_filters(df):
    st.sidebar.header("Filters")

    available_difficulties = [d for d in DIFFICULTY_ORDER if d in df["difficulty"].unique()]
    selected_difficulties = st.sidebar.multiselect(
        "Difficulty", options=available_difficulties, default=available_difficulties
    )

    solved_options = sorted(df["solved"].unique().tolist())
    selected_solved = st.sidebar.multiselect(
        "Solved Status",
        options=solved_options,
        default=solved_options,
        format_func=lambda v: "Solved" if v == 1 else "Unsolved",
    )

    id_min, id_max = int(df["id"].min()), int(df["id"].max())
    id_range = st.sidebar.slider("Puzzle ID Range", min_value=id_min, max_value=id_max, value=(id_min, id_max))

    filtered = df[
        df["difficulty"].isin(selected_difficulties)
        & df["solved"].isin(selected_solved)
        & df["id"].between(id_range[0], id_range[1])
    ]

    st.sidebar.markdown(f"**{len(filtered)}** of **{len(df)}** puzzles selected")
    return filtered


def render_kpi_cards(df):
    solve_rate = df["solved"].mean() * 100
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Puzzles", len(df))
    c2.metric("Avg Recursive Calls", f"{df['recursive_calls'].mean():,.0f}")
    c3.metric("Avg Backtracks", f"{df['backtracks'].mean():,.0f}")
    c4.metric("Avg Execution Time", f"{df['execution_time_ms'].mean():.3f} ms")
    c5.metric("Solve Rate", f"{solve_rate:.1f}%")


def missing_results_notice():
    st.warning(
        f"No results found at `{RESULTS_PATH}`. Run the C benchmark and dataset "
        "pipeline first, then reload this page."
    )


# =========================================================
# Pages
# =========================================================


def _compute_home_kpis(results_df):
    """Total puzzles, average runtime, average recursive calls, and the R² of
    a simple empty_cells -> recursive_calls linear fit, computed on the full
    (unfiltered) results dataset."""
    if results_df is None or results_df.empty:
        return None

    total_puzzles = len(results_df)
    avg_runtime = results_df["execution_time_ms"].mean()
    avg_calls = results_df["recursive_calls"].mean()

    r_squared = None
    if total_puzzles >= 2:
        x = results_df["empty_cells"].to_numpy(dtype=float)
        y = results_df["recursive_calls"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        predicted = slope * x + intercept
        ss_res = float(np.sum((y - predicted) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {
        "total_puzzles": total_puzzles,
        "avg_runtime": avg_runtime,
        "avg_calls": avg_calls,
        "r_squared": r_squared,
    }


def _card_grid(cards, css_class="sil-card"):
    """Render a row of equally-sized cards, one per dict with 'title' and
    'desc' keys, using the given CSS class."""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="{css_class}"><h4>{card["title"]}</h4>'
                f'<p>{card["desc"]}</p></div>',
                unsafe_allow_html=True,
            )


def _pipeline_diagram_svg(steps):
    box_w, box_h, gap, margin = 150, 44, 32, 10
    n = len(steps)
    total_w = n * box_w + (n - 1) * gap
    canvas_w = total_w + 2 * margin
    canvas_h = box_h + 2 * margin
    cy = margin + box_h / 2

    parts = [
        f'<svg viewBox="0 0 {canvas_w} {canvas_h}" width="100%" '
        f'style="max-width:{canvas_w}px; display:block;" '
        'xmlns="http://www.w3.org/2000/svg">'
    ]

    for i, label in enumerate(steps):
        x = margin + i * (box_w + gap)
        parts.append(
            f'<rect x="{x}" y="{margin}" width="{box_w}" height="{box_h}" rx="6" '
            f'fill="{BG_CARD}" stroke="rgba(255,255,255,0.16)" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{x + box_w / 2}" y="{cy + 4}" text-anchor="middle" '
            f'font-family="-apple-system, Segoe UI, Roboto, Arial, sans-serif" '
            f'font-size="12.5" font-weight="500" fill="{TEXT}">{label}</text>'
        )
        if i != n - 1:
            line_x0 = x + box_w
            line_x1 = x + box_w + gap - 6
            parts.append(
                f'<line x1="{line_x0}" y1="{cy}" x2="{line_x1}" y2="{cy}" '
                f'stroke="{ACCENT}" stroke-width="1.5" />'
            )
            parts.append(
                f'<polygon points="{line_x1},{cy - 4} {line_x1 + 6},{cy} {line_x1},{cy + 4}" '
                f'fill="{ACCENT}" />'
            )

    parts.append("</svg>")
    return "".join(parts)


def page_home(results_df, puzzles_df):
    st.title("Sudoku Intelligence Lab")
    st.markdown(
        '<p class="sil-meta">Implemented in C • 1000 benchmark puzzles • '
        "Performance instrumentation • Streamlit</p>",
        unsafe_allow_html=True,
    )

    # ---------------- Hero: board + KPIs ----------------
    board_col, kpi_col = st.columns([1, 1], gap="large")

    with board_col:
        st.markdown('<div class="sil-section-label">Puzzle Preview</div>', unsafe_allow_html=True)
        if puzzles_df is not None and not puzzles_df.empty:
            sample_row = puzzles_df.sample(1, random_state=None).iloc[0]
            grid = get_grid_from_string(sample_row["puzzle"])
            display_board(grid, title=f"Puzzle #{sample_row['id']}", size=500)
        else:
            display_board(string_to_grid_fallback(DEMO_PUZZLE), title="Sample Puzzle", size=500)

    with kpi_col:
        st.markdown('<div class="sil-hero-panel">', unsafe_allow_html=True)
        st.markdown('<div class="sil-section-label">Overview</div>', unsafe_allow_html=True)

        kpis = _compute_home_kpis(results_df)
        if kpis is None:
            missing_results_notice()
        else:
            row1c1, row1c2 = st.columns(2, gap="medium")
            row1c1.metric("Total Puzzles", f"{kpis['total_puzzles']:,}")
            row1c2.metric("Avg Runtime", f"{kpis['avg_runtime']:.3f} ms")

            row2c1, row2c2 = st.columns(2, gap="medium")
            row2c1.metric("Avg Recursive Calls", f"{kpis['avg_calls']:,.0f}")
            r2_display = f"{kpis['r_squared']:.3f}" if kpis["r_squared"] is not None else "—"
            row2c2.metric("Regression R²", r2_display)

            st.caption(
                "R² is for a linear fit of recursive calls against empty cells "
                "across the full benchmark dataset."
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ---------------- Capabilities: typography only, no cards ----------------
    st.markdown('<div class="sil-section-label">Capabilities</div>', unsafe_allow_html=True)
    capabilities = [
        {
            "title": "C Solver",
            "desc": "Recursive backtracking implementation with performance instrumentation.",
        },
        {
            "title": "Performance Instrumentation",
            "desc": "Tracks recursive calls, backtracks, and candidate checks.",
        },
        {
            "title": "Statistical Analysis",
            "desc": "Distributions and correlations across solver metrics.",
        },
        {
            "title": "Numerical Methods & Regression",
            "desc": "Linear fits and predictive models built on the results.",
        },
    ]
    spec_html = ['<div class="sil-spec-grid">']
    for item in capabilities:
        spec_html.append(
            f'<div class="sil-spec-cell"><h4>{item["title"]}</h4><p>{item["desc"]}</p></div>'
        )
    spec_html.append("</div>")
    st.markdown("".join(spec_html), unsafe_allow_html=True)

    st.divider()

    # ---------------- Key Findings ----------------
    st.markdown('<div class="sil-section-label">Key Findings</div>', unsafe_allow_html=True)
    if results_df is None or results_df.empty:
        missing_results_notice()
    else:
        corr_empty_calls = (
            results_df["empty_cells"].corr(results_df["recursive_calls"])
            if len(results_df) > 1
            else float("nan")
        )
        by_difficulty = (
            results_df.groupby("difficulty")["execution_time_ms"]
            .mean()
            .reindex(DIFFICULTY_ORDER)
            .dropna()
        )
        if len(by_difficulty) >= 2:
            multiplier = by_difficulty.iloc[-1] / max(by_difficulty.iloc[0], 1e-9)
            multiplier_text = f"~{multiplier:.1f}x higher execution time for Expert versus Easy puzzles."
        else:
            multiplier_text = "Not enough difficulty tiers in the current data to compare."

        backtrack_ratio = (
            results_df["backtracks"] / results_df["recursive_calls"].replace(0, np.nan)
        ).mean() * 100

        _card_grid(
            [
                {
                    "title": "Search space scales with puzzle complexity",
                    "desc": f"Empty cells and recursive calls correlate at r = {corr_empty_calls:.2f}.",
                },
                {
                    "title": "Execution time scales with difficulty",
                    "desc": multiplier_text,
                },
                {
                    "title": "Backtracking overhead",
                    "desc": f"Backtracks account for about {backtrack_ratio:.1f}% of recursive calls on average.",
                },
            ],
            css_class="sil-finding",
        )

    st.divider()

    # ---------------- Architecture ----------------
    st.markdown('<div class="sil-section-label">Architecture</div>', unsafe_allow_html=True)
    steps = [
        "Puzzle Dataset",
        "C Solver",
        "Performance Metrics",
        "Python Analytics",
        "Interactive Dashboard",
    ]
    st.markdown(_pipeline_diagram_svg(steps), unsafe_allow_html=True)


def page_explorer(results_df, puzzles_df):
    # Page-scoped typography boost (~10% larger) — does not affect other pages.
    st.markdown(
        f"""
        <style>
            .sil-explorer h1 {{ font-size: 1.76rem; }}
            .sil-explorer .stCaption, .sil-explorer [data-testid="stCaptionContainer"] {{
                font-size: 0.94rem !important;
            }}
            .sil-explorer .sil-section-label {{ font-size: 0.79rem; }}
            .sil-explorer .stSelectbox label {{ font-size: 1.1rem; font-weight: 600; }}
            .sil-explorer div[data-baseweb="select"] {{ font-size: 1.1rem; }}
            .sil-explorer .stButton>button {{ font-size: 1.05rem; padding: 0.5rem 1rem; }}
            .sil-explorer div[data-testid="stMetricLabel"] {{ font-size: 0.86rem; }}
            .sil-explorer div[data-testid="stMetricValue"] {{ font-size: 1.65rem; }}
        </style>
        <div class="sil-explorer">
        """,
        unsafe_allow_html=True,
    )

    st.title("Explorer")
    st.caption("Inspect a single benchmarked puzzle: original, solved, and solver metrics.")

    # ---------------- Puzzle selector ----------------
    if puzzles_df is None or puzzles_df.empty:
        st.warning(f"No puzzle dataset found at `{PUZZLES_PATH}`. Showing a demo puzzle instead.")
        selected_id = "demo"
        puzzle_str = DEMO_PUZZLE
    else:
        ids = puzzles_df["id"].tolist()

        top_l, top_r = st.columns([4, 1])
        with top_l:
            selected_id = st.selectbox("Select puzzle ID", options=ids, index=0)
        with top_r:
            st.write("")
            if st.button("Random puzzle"):
                selected_id = int(np.random.choice(ids))

        puzzle_str = puzzles_df.loc[puzzles_df["id"] == selected_id, "puzzle"].iloc[0]

    grid = get_grid_from_string(puzzle_str)
    solution = get_solution(grid, puzzle_str)

    match = None
    if results_df is not None and selected_id != "demo":
        candidate = results_df.loc[results_df["id"] == selected_id]
        if not candidate.empty:
            match = candidate.iloc[0]

    # ---------------- Metadata ----------------
    st.markdown('<div class="sil-section-label">Puzzle Metadata</div>', unsafe_allow_html=True)
    meta_id = "Demo" if selected_id == "demo" else selected_id
    meta_difficulty = derive_difficulty(selected_id) if selected_id != "demo" else "—"
    if match is not None:
        meta_solved = "Solved" if match["solved"] == 1 else "Not Solved"
    else:
        meta_solved = "—"

    meta1, meta2, meta3 = st.columns(3)
    meta1.metric("Puzzle ID", meta_id)
    meta2.metric("Difficulty", meta_difficulty)
    meta3.metric("Status", meta_solved)

    st.divider()

    # ---------------- Boards, equal size, side by side ----------------
    left, right = st.columns(2)
    with left:
        display_board(grid, title="Original Puzzle", size=420)
    with right:
        if solution is not None:
            display_board(solution, title="Solved Puzzle", size=420)
        else:
            st.error("This puzzle could not be solved by the fallback solver.")

    # ---------------- Performance Summary ----------------
    st.divider()
    st.markdown('<div class="sil-section-label">Performance Summary</div>', unsafe_allow_html=True)
    if match is None:
        missing_results_notice()
    else:
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("Recursive Calls", f"{match['recursive_calls']:,}")
        p2.metric("Backtracks", f"{match['backtracks']:,}")
        p3.metric("Candidate Checks", f"{match['candidate_checks']:,}")
        p4.metric("Execution Time", f"{match['execution_time_ms']:.3f} ms")
        p5.metric("Maximum Depth", f"{match['maximum_depth']:,}")

    st.markdown("</div>", unsafe_allow_html=True)


def page_performance(df):
    # Page-scoped typography boost (~10%) — does not affect other pages.
    st.markdown(
        f"""
        <style>
            .sil-performance h1 {{ font-size: 1.76rem; }}
            .sil-performance h2, .sil-performance h3 {{ font-size: 1.16rem; }}
            .sil-performance .sil-section-label {{ font-size: 0.79rem; }}
            .sil-performance .stCaption, .sil-performance [data-testid="stCaptionContainer"] {{
                font-size: 0.94rem !important;
            }}
            .sil-performance div[data-testid="stMetricLabel"] {{ font-size: 0.86rem; }}
            .sil-performance div[data-testid="stMetricValue"] {{ font-size: 1.65rem; }}
            .sil-performance p, .sil-performance li {{ font-size: 1rem; }}

            .sil-finding-text {{
                margin: 4px 0 10px 0;
                font-size: 0.92rem;
                line-height: 1.5;
            }}
            .sil-finding-text .label {{
                color: {TEXT_MUTED};
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.72rem;
                letter-spacing: 0.05em;
                margin-right: 6px;
            }}
        </style>
        <div class="sil-performance">
        """,
        unsafe_allow_html=True,
    )

    st.title("Performance")
    if df is None:
        missing_results_notice()
        st.markdown("</div>", unsafe_allow_html=True)
        return
    if df.empty:
        st.info("No puzzles match the current filters. Adjust the filters in the sidebar.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    render_kpi_cards(df)
    st.divider()

    def report_block(finding, evidence, conclusion):
        st.markdown(
            f'<p class="sil-finding-text"><span class="label">Finding</span>{finding}</p>'
            f'<p class="sil-finding-text"><span class="label">Evidence</span>{evidence}</p>'
            f'<p class="sil-finding-text"><span class="label">Conclusion</span>{conclusion}</p>',
            unsafe_allow_html=True,
        )

    # ---------------- Precompute report statistics (display-only) ----------------
    by_diff_calls = df.groupby("difficulty")["recursive_calls"].median().reindex(DIFFICULTY_ORDER).dropna()
    by_diff_time = df.groupby("difficulty")["execution_time_ms"].median().reindex(DIFFICULTY_ORDER).dropna()
    corr_time_calls = df["execution_time_ms"].corr(df["recursive_calls"]) if len(df) > 1 else float("nan")
    skew_calls = df["recursive_calls"].skew() if len(df) > 2 else float("nan")

    top10 = df.sort_values("recursive_calls", ascending=False).head(10)
    top10_expert_share = (top10["difficulty"] == "Expert").sum()

    # ---------------- 1. Distribution of Recursive Calls ----------------
    st.subheader("Recursive Call Distribution Is Right-Skewed")
    report_block(
        "Most puzzles solve with relatively few recursive calls, but a small "
        "number require far more.",
        f"Skewness of recursive calls is {skew_calls:.2f} "
        f"(mean {df['recursive_calls'].mean():,.0f}, median {df['recursive_calls'].median():,.0f}).",
        "A long right tail means a handful of puzzles dominate total solver cost, "
        "so average-based capacity planning can understate worst-case load.",
    )
    fig = px.histogram(
        df, x="recursive_calls", nbins=30,
        labels={"recursive_calls": "Recursive Calls"},
        color_discrete_sequence=[ACCENT],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- 2. Recursive Calls by Difficulty ----------------
    st.subheader("Difficulty Tier Separates Recursive Call Cost")
    if len(by_diff_calls) >= 2:
        calls_evidence = (
            f"Median recursive calls range from {by_diff_calls.iloc[0]:,.0f} (Easy) "
            f"to {by_diff_calls.iloc[-1]:,.0f} (Expert)."
        )
    else:
        calls_evidence = "Not enough difficulty tiers in the current selection to compare."
    report_block(
        "Recursive call counts increase consistently across difficulty tiers.",
        calls_evidence,
        "Difficulty tier is a reliable grouping variable for solver cost and can "
        "be used to set expectations for search effort before solving.",
    )
    fig = px.box(
        df, x="difficulty", y="recursive_calls", color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        color_discrete_map=DIFFICULTY_COLORS,
        labels={"difficulty": "Difficulty", "recursive_calls": "Recursive Calls"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- 3. Execution Time by Difficulty ----------------
    st.subheader("Execution Time Scales With Difficulty, With More Spread")
    if len(by_diff_time) >= 2:
        time_evidence = (
            f"Median execution time ranges from {by_diff_time.iloc[0]:.3f} ms (Easy) "
            f"to {by_diff_time.iloc[-1]:.3f} ms (Expert)."
        )
    else:
        time_evidence = "Not enough difficulty tiers in the current selection to compare."
    report_block(
        "Execution time rises with difficulty but with wider variability than "
        "recursive calls alone.",
        time_evidence,
        "Difficulty predicts typical runtime, but system-level timing noise means "
        "recursive calls remain the more stable metric for cost estimation.",
    )
    fig = px.box(
        df, x="difficulty", y="execution_time_ms", color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        color_discrete_map=DIFFICULTY_COLORS,
        labels={"difficulty": "Difficulty", "execution_time_ms": "Execution Time (ms)"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- 4. Runtime vs Recursive Calls ----------------
    st.subheader("Recursive Calls Are a Strong Predictor of Runtime")
    corr_text = f"r = {corr_time_calls:.2f}" if not np.isnan(corr_time_calls) else "not available"
    report_block(
        "Execution time closely tracks the number of recursive calls a puzzle "
        "requires.",
        f"Execution time correlates with recursive calls at {corr_text} across "
        f"{len(df)} puzzles.",
        "Recursive call count is a practical, low-noise stand-in for wall-clock "
        "cost when profiling or comparing puzzles.",
    )
    fig = px.scatter(
        df, x="recursive_calls", y="execution_time_ms", color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        color_discrete_map=DIFFICULTY_COLORS,
        labels={"recursive_calls": "Recursive Calls", "execution_time_ms": "Execution Time (ms)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- 5. Top 10 Hardest Puzzles ----------------
    st.subheader("Hardest Puzzles Cluster in the Expert Tier")
    report_block(
        "The puzzles with the highest recursive call counts are concentrated in "
        "the hardest difficulty tier.",
        f"{top10_expert_share} of the top 10 puzzles by recursive calls are "
        "labeled Expert.",
        "Generation difficulty labels align with actual measured solver cost, "
        "validating difficulty tier as a trustworthy benchmark grouping.",
    )
    st.dataframe(
        top10[["id", "difficulty", "recursive_calls", "backtracks", "execution_time_ms"]].rename(
            columns={
                "id": "Puzzle ID",
                "difficulty": "Difficulty",
                "recursive_calls": "Recursive Calls",
                "backtracks": "Backtracks",
                "execution_time_ms": "Execution Time (ms)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.download_button(
        "Download filtered dataset as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sudoku_results.csv",
        mime="text/csv",
    )

    st.markdown("</div>", unsafe_allow_html=True)


def page_statistics(df):
    # Page-scoped typography boost (slight, ~5%) — does not affect other pages.
    st.markdown(
        f"""
        <style>
            .sil-statistics h1 {{ font-size: 1.68rem; }}
            .sil-statistics h2, .sil-statistics h3 {{ font-size: 1.1rem; }}
            .sil-statistics .sil-section-label {{ font-size: 0.76rem; }}
            .sil-statistics .stCaption, .sil-statistics [data-testid="stCaptionContainer"] {{
                font-size: 0.89rem !important;
            }}
            .sil-statistics div[data-testid="stMetricLabel"] {{ font-size: 0.82rem; }}
            .sil-statistics div[data-testid="stMetricValue"] {{ font-size: 1.58rem; }}
            .sil-statistics p, .sil-statistics li {{ font-size: 1.02rem; }}

            .sil-finding-text {{
                margin: 4px 0 10px 0;
                font-size: 0.94rem;
                line-height: 1.5;
            }}
            .sil-finding-text .label {{
                color: {TEXT_MUTED};
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.74rem;
                letter-spacing: 0.05em;
                margin-right: 6px;
            }}
            .sil-question {{
                color: {TEXT_MUTED};
                font-size: 0.95rem;
                font-style: italic;
                margin: -4px 0 14px 0;
            }}
        </style>
        <div class="sil-statistics">
        """,
        unsafe_allow_html=True,
    )

    st.title("Statistics")
    if df is None:
        missing_results_notice()
        st.markdown("</div>", unsafe_allow_html=True)
        return
    if df.empty:
        st.info("No puzzles match the current filters. Adjust the filters in the sidebar.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    def report_block(finding, evidence, conclusion):
        st.markdown(
            f'<p class="sil-finding-text"><span class="label">Finding</span>{finding}</p>'
            f'<p class="sil-finding-text"><span class="label">Evidence</span>{evidence}</p>'
            f'<p class="sil-finding-text"><span class="label">Conclusion</span>{conclusion}</p>',
            unsafe_allow_html=True,
        )

    numeric_columns = [c for c in NUMERIC_METRICS if c in df.columns]

    # ============================================================
    # Section 1 — How does puzzle difficulty affect solver complexity?
    # ============================================================
    st.markdown('<div class="sil-section-label">Section 1</div>', unsafe_allow_html=True)
    st.subheader("How Does Puzzle Difficulty Affect Solver Complexity?")

    by_diff_calls = df.groupby("difficulty")["recursive_calls"].median().reindex(DIFFICULTY_ORDER).dropna()
    by_diff_time = df.groupby("difficulty")["execution_time_ms"].median().reindex(DIFFICULTY_ORDER).dropna()
    if len(by_diff_calls) >= 2 and len(by_diff_time) >= 2:
        s1_evidence = (
            f"Median recursive calls rise from {by_diff_calls.iloc[0]:,.0f} (Easy) to "
            f"{by_diff_calls.iloc[-1]:,.0f} (Expert); median execution time rises from "
            f"{by_diff_time.iloc[0]:.3f} ms to {by_diff_time.iloc[-1]:.3f} ms over the same tiers."
        )
    else:
        s1_evidence = "Not enough difficulty tiers in the current selection to compare."
    report_block(
        "Both recursive calls and execution time increase consistently as puzzle "
        "difficulty rises.",
        s1_evidence,
        "Difficulty tier is a reliable predictor of solver complexity across both "
        "a computation-based metric (recursive calls) and a wall-clock metric "
        "(execution time).",
    )

    dist1, dist2 = st.columns(2)
    with dist1:
        fig = px.box(
            df, x="difficulty", y="recursive_calls", color="difficulty",
            category_orders={"difficulty": DIFFICULTY_ORDER},
            color_discrete_map=DIFFICULTY_COLORS,
            title="Recursive Calls by Difficulty",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with dist2:
        fig = px.box(
            df, x="difficulty", y="execution_time_ms", color="difficulty",
            category_orders={"difficulty": DIFFICULTY_ORDER},
            color_discrete_map=DIFFICULTY_COLORS,
            title="Execution Time by Difficulty",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ============================================================
    # Section 2 — Which metrics are most strongly related?
    # ============================================================
    st.markdown('<div class="sil-section-label">Section 2</div>', unsafe_allow_html=True)
    st.subheader("Which Metrics Are Most Strongly Related?")

    if len(df) > 1 and len(numeric_columns) > 1:
        corr_matrix = df[numeric_columns].corr()
        mask = np.triu(np.ones(corr_matrix.shape, dtype=bool), k=1)
        pairs = corr_matrix.where(mask).unstack().dropna()

        if len(pairs) > 0:
            strongest_key = pairs.abs().idxmax()
            weakest_key = pairs.abs().idxmin()
            strongest_val = pairs[strongest_key]
            weakest_val = pairs[weakest_key]
            s2_evidence = (
                f"Strongest relationship: {strongest_key[0]} vs {strongest_key[1]} "
                f"(r = {strongest_val:.2f}). Weakest relationship: {weakest_key[0]} vs "
                f"{weakest_key[1]} (r = {weakest_val:.2f})."
            )
        else:
            s2_evidence = "Not enough metric pairs to compare."

        report_block(
            "Solver metrics vary widely in how closely they move together.",
            s2_evidence,
            "The strongest pair points to the most redundant metric for tracking "
            "solver cost, while the weakest pair marks metrics that carry mostly "
            "independent information.",
        )

        fig = px.imshow(
            corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1, title="Metric Correlation Heatmap",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to compute correlations.")

    st.divider()

    # ============================================================
    # Section 3 — Can recursive calls explain execution time?
    # ============================================================
    st.markdown('<div class="sil-section-label">Section 3</div>', unsafe_allow_html=True)
    st.subheader("Can Recursive Calls Explain Execution Time?")

    corr_calls_time = df["execution_time_ms"].corr(df["recursive_calls"]) if len(df) > 1 else float("nan")
    corr_calls_time_text = f"r = {corr_calls_time:.2f}" if not np.isnan(corr_calls_time) else "not available"
    report_block(
        "Execution time closely follows the number of recursive calls a puzzle requires.",
        f"The correlation between recursive calls and execution time is {corr_calls_time_text} "
        f"across {len(df)} puzzles.",
        "Recursive calls explain most of the variation in execution time, making "
        "them a dependable proxy for runtime when comparing puzzles.",
    )
    fig = px.scatter(
        df, x="recursive_calls", y="execution_time_ms", color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        color_discrete_map=DIFFICULTY_COLORS,
        trendline="ols" if len(df) > 1 else None,
        title="Execution Time vs. Recursive Calls",
        labels={"recursive_calls": "Recursive Calls", "execution_time_ms": "Execution Time (ms)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ============================================================
    # Section 4 — Do empty cells predict solver cost?
    # ============================================================
    st.markdown('<div class="sil-section-label">Section 4</div>', unsafe_allow_html=True)
    st.subheader("Do Empty Cells Predict Solver Cost?")

    corr_empty_calls = df["empty_cells"].corr(df["recursive_calls"]) if len(df) > 1 else float("nan")
    corr_empty_calls_text = f"r = {corr_empty_calls:.2f}" if not np.isnan(corr_empty_calls) else "not available"
    report_block(
        "The number of empty cells has only a weak relationship with recursive calls.",
        f"The correlation between empty cells and recursive calls is {corr_empty_calls_text}, "
        "noticeably weaker than the relationship between recursive calls and execution time.",
        "Empty cell count sets the size of the search space but not its shape: two "
        "puzzles with the same number of empty cells can differ greatly in how "
        "constrained those cells are, so cell count alone is a poor predictor of "
        "solver cost.",
    )
    fig = px.scatter(
        df, x="empty_cells", y="recursive_calls", color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        color_discrete_map=DIFFICULTY_COLORS,
        trendline="ols" if len(df) > 1 else None,
        title="Empty Cells vs. Recursive Calls",
        labels={"empty_cells": "Empty Cells", "recursive_calls": "Recursive Calls"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _fit_linear(df, x_col, y_col):
    """Same linear-fit math as before (np.polyfit least squares), just
    factored into a helper so both regression studies share one calculation."""
    x = df[x_col].to_numpy(dtype=float)
    y = df[y_col].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    residuals = y - predicted
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    correlation = float(np.corrcoef(x, y)[0, 1]) if len(x) > 1 else 0.0
    return {
        "x": x, "y": y, "slope": slope, "intercept": intercept,
        "r_squared": r_squared, "correlation": correlation,
    }


def page_regression(df):
    # Page-scoped typography boost (slight, ~5%) — does not affect other pages.
    st.markdown(
        f"""
        <style>
            .sil-regression h1 {{ font-size: 1.68rem; }}
            .sil-regression h2, .sil-regression h3 {{ font-size: 1.1rem; }}
            .sil-regression .sil-section-label {{ font-size: 0.76rem; }}
            .sil-regression .stCaption, .sil-regression [data-testid="stCaptionContainer"] {{
                font-size: 0.89rem !important;
            }}
            .sil-regression div[data-testid="stMetricLabel"] {{ font-size: 0.82rem; }}
            .sil-regression div[data-testid="stMetricValue"] {{ font-size: 1.58rem; }}
            .sil-regression p, .sil-regression li {{ font-size: 1.02rem; }}

            .sil-question {{
                color: {TEXT_MUTED};
                font-size: 0.95rem;
                font-style: italic;
                margin: -4px 0 14px 0;
            }}
            .sil-finding-text {{
                margin: 4px 0 10px 0;
                font-size: 0.94rem;
                line-height: 1.5;
            }}
            .sil-finding-text .label {{
                color: {TEXT_MUTED};
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.74rem;
                letter-spacing: 0.05em;
                margin-right: 6px;
            }}
        </style>
        <div class="sil-regression">
        """,
        unsafe_allow_html=True,
    )

    st.title("Regression")
    if df is None:
        missing_results_notice()
        st.markdown("</div>", unsafe_allow_html=True)
        return
    if df.empty:
        st.info("No puzzles match the current filters. Adjust the filters in the sidebar.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    if len(df) < 2:
        st.info("Need at least two puzzles to fit a regression line.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    def render_study(x_col, y_col, x_label, y_label, chart_title, conclusion, show_slope):
        fit = _fit_linear(df, x_col, y_col)

        metric_cols = st.columns(3 if show_slope else 2)
        metric_cols[0].metric("R²", f"{fit['r_squared']:.3f}")
        metric_cols[1].metric("Correlation (r)", f"{fit['correlation']:.3f}")
        if show_slope:
            metric_cols[2].metric("Slope", f"{fit['slope']:.3f}")

        st.markdown(
            f'<p class="sil-finding-text"><span class="label">Conclusion</span>{conclusion}</p>',
            unsafe_allow_html=True,
        )

        fig = px.scatter(
            df, x=x_col, y=y_col, color="difficulty",
            category_orders={"difficulty": DIFFICULTY_ORDER},
            color_discrete_map=DIFFICULTY_COLORS,
            title=chart_title,
            labels={x_col: x_label, y_col: y_label},
        )
        line_x = np.linspace(fit["x"].min(), fit["x"].max(), 100)
        line_y = fit["slope"] * line_x + fit["intercept"]
        fig.add_trace(
            go.Scatter(x=line_x, y=line_y, mode="lines", name="Fitted line", line=dict(color=ACCENT, width=3))
        )
        st.plotly_chart(fig, use_container_width=True)

        return fit

    # ============================================================
    # Study 1 — Can empty cell count predict recursive search effort?
    # ============================================================
    st.markdown('<div class="sil-section-label">Study 1</div>', unsafe_allow_html=True)
    st.subheader("Can Empty Cell Count Predict Recursive Search Effort?")
    fit1 = render_study(
        "empty_cells", "recursive_calls",
        "Empty Cells", "Recursive Calls",
        "Recursive Calls vs. Empty Cells",
        "The model explains only a small share of the variation in recursive calls. "
        "Empty cell count sets the raw size of the search space but says nothing "
        "about how constrained those cells are, so puzzles with similar empty-cell "
        "counts can require very different amounts of search.",
        show_slope=True,
    )

    st.divider()

    # ============================================================
    # Study 2 — Can recursive calls predict execution time?
    # ============================================================
    st.markdown('<div class="sil-section-label">Study 2</div>', unsafe_allow_html=True)
    st.subheader("Can Recursive Calls Predict Execution Time?")
    fit2 = render_study(
        "recursive_calls", "execution_time_ms",
        "Recursive Calls", "Execution Time (ms)",
        "Execution Time vs. Recursive Calls",
        "The model explains most of the variation in execution time. Each recursive "
        "call does a bounded, roughly constant amount of work, so the total call "
        "count scales almost linearly with wall-clock runtime.",
        show_slope=False,
    )

    st.divider()

    # ============================================================
    # Comparison
    # ============================================================
    st.markdown('<div class="sil-section-label">Comparison</div>', unsafe_allow_html=True)
    st.subheader("Which Predictor Is Stronger?")

    comparison = pd.DataFrame(
        [
            {
                "Model": "Study 1",
                "Predictor": "Empty Cells",
                "Target": "Recursive Calls",
                "R²": round(fit1["r_squared"], 3),
                "Correlation (r)": round(fit1["correlation"], 3),
            },
            {
                "Model": "Study 2",
                "Predictor": "Recursive Calls",
                "Target": "Execution Time",
                "R²": round(fit2["r_squared"], 3),
                "Correlation (r)": round(fit2["correlation"], 3),
            },
        ]
    )
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    if fit2["r_squared"] >= fit1["r_squared"]:
        stronger_text = (
            f"Recursive calls are the stronger predictor overall (R² = {fit2['r_squared']:.3f} "
            f"for execution time vs. R² = {fit1['r_squared']:.3f} for empty cells predicting "
            "recursive calls), making them the more dependable metric for estimating solver cost."
        )
    else:
        stronger_text = (
            f"Empty cells are the stronger predictor in this comparison (R² = {fit1['r_squared']:.3f} "
            f"vs. R² = {fit2['r_squared']:.3f})."
        )
    st.markdown(f'<p class="sil-finding-text">{stronger_text}</p>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def page_prediction(df):
    # Page-scoped typography boost (slight, ~5%) — does not affect other pages.
    st.markdown(
        f"""
        <style>
            .sil-prediction h1 {{ font-size: 1.68rem; }}
            .sil-prediction h2, .sil-prediction h3 {{ font-size: 1.1rem; }}
            .sil-prediction .sil-section-label {{ font-size: 0.76rem; }}
            .sil-prediction .stCaption, .sil-prediction [data-testid="stCaptionContainer"] {{
                font-size: 0.89rem !important;
            }}
            .sil-prediction div[data-testid="stMetricLabel"] {{ font-size: 0.82rem; }}
            .sil-prediction div[data-testid="stMetricValue"] {{ font-size: 1.58rem; }}
            .sil-prediction p, .sil-prediction li {{ font-size: 1.02rem; }}

            .sil-finding-text {{
                margin: 4px 0 10px 0;
                font-size: 0.94rem;
                line-height: 1.5;
            }}
            .sil-finding-text .label {{
                color: {TEXT_MUTED};
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.74rem;
                letter-spacing: 0.05em;
                margin-right: 6px;
            }}

            .sil-summary-card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 3px solid {ACCENT};
                border-radius: 8px;
                padding: 18px 20px;
            }}
            .sil-summary-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px 18px;
            }}
            .sil-summary-grid .label {{
                display: block;
                font-size: 0.72rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {TEXT_MUTED};
                margin-bottom: 2px;
            }}
            .sil-summary-grid .value {{
                display: block;
                font-size: 1.15rem;
                font-weight: 600;
                color: {TEXT};
            }}

            .sil-notes {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 16px 20px;
                color: {TEXT_MUTED};
                font-size: 0.9rem;
                line-height: 1.55;
            }}
        </style>
        <div class="sil-prediction">
        """,
        unsafe_allow_html=True,
    )

    st.title("Prediction")
    st.caption("Estimate solver effort from puzzle characteristics using a simple linear fit.")

    if df is None:
        missing_results_notice()
        st.markdown("</div>", unsafe_allow_html=True)
        return
    if df.empty or len(df) < 2:
        st.info("Not enough data to build a prediction model.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    target_options = [c for c in NUMERIC_METRICS if c in df.columns and c != "empty_cells"]
    target_col = st.selectbox("Metric to predict", target_options, index=target_options.index("recursive_calls"))
    target_label = target_col.replace("_", " ")

    x = df["empty_cells"].to_numpy(dtype=float)
    y = df[target_col].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)

    predicted_all = slope * x + intercept
    ss_res = float(np.sum((y - predicted_all) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    empty_min, empty_max = int(x.min()), int(x.max())
    empty_input = st.slider("Empty cells", min_value=empty_min, max_value=empty_max, value=int(x.mean()))

    prediction = slope * empty_input + intercept
    prediction = max(prediction, 0)

    # ---------------- Confidence + approximate difficulty (display-only) ----------------
    if r_squared >= 0.7:
        confidence = "High"
    elif r_squared >= 0.4:
        confidence = "Medium"
    else:
        confidence = "Low"

    by_diff_empty = df.groupby("difficulty")["empty_cells"].median().reindex(DIFFICULTY_ORDER).dropna()
    if len(by_diff_empty) > 0:
        expected_difficulty = (by_diff_empty - empty_input).abs().idxmin()
    else:
        expected_difficulty = "—"

    # ---------------- Finding / Interpretation / Conclusion ----------------
    st.markdown('<div class="sil-section-label">Reading This Prediction</div>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="sil-finding-text"><span class="label">Finding</span>'
        f"At {empty_input} empty cells, the model predicts a {target_label} of "
        f"{prediction:,.1f}.</p>"
        f'<p class="sil-finding-text"><span class="label">Interpretation</span>'
        f"Each additional empty cell shifts predicted {target_label} by about "
        f"{slope:,.2f} on this linear fit, which explains {r_squared:.3f} of the "
        f"variation ({r_squared * 100:.0f}%) seen in the dataset.</p>"
        f'<p class="sil-finding-text"><span class="label">Conclusion</span>'
        f"Treat this as a {confidence.lower()}-confidence estimate — useful for "
        "spotting trends, not a substitute for actually running the solver.</p>",
        unsafe_allow_html=True,
    )

    # ---------------- Prediction Summary card ----------------
    st.markdown(
        '<div class="sil-summary-card">'
        '<div class="sil-summary-grid">'
        f'<div><span class="label">Predicted {target_label}</span>'
        f'<span class="value">{prediction:,.1f}</span></div>'
        '<div><span class="label">Expected Difficulty (approx.)</span>'
        f'<span class="value">{expected_difficulty}</span></div>'
        '<div><span class="label">Model Confidence</span>'
        f'<span class="value">{confidence}</span></div>'
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.write("")

    fig = px.scatter(
        df, x="empty_cells", y=target_col, color="difficulty",
        category_orders={"difficulty": DIFFICULTY_ORDER},
        color_discrete_map=DIFFICULTY_COLORS,
        title=f"{target_col} vs. Empty Cells",
    )
    line_x = np.linspace(empty_min, empty_max, 100)
    line_y = slope * line_x + intercept
    fig.add_trace(go.Scatter(x=line_x, y=line_y, mode="lines", name="Fitted line", line=dict(color=ACCENT, width=3)))
    fig.add_trace(
        go.Scatter(
            x=[empty_input], y=[prediction], mode="markers", name="Prediction",
            marker=dict(color="#FFFFFF", size=14, line=dict(color=ACCENT, width=3), symbol="star"),
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------- Model Notes (replaces the old footer disclaimer) ----------------
    st.markdown('<div class="sil-section-label">Model Notes</div>', unsafe_allow_html=True)
    if confidence == "High":
        notes_text = (
            f"R² = {r_squared:.3f} — empty cell count explains most of the variation in "
            f"{target_label} here, so the fitted line tracks the data closely and the "
            "prediction above is a reasonably reliable estimate."
        )
    elif confidence == "Medium":
        notes_text = (
            f"R² = {r_squared:.3f} — empty cell count explains a moderate share of the "
            f"variation in {target_label}. The trend direction is meaningful, but individual "
            "predictions can be noticeably off for any single puzzle."
        )
    else:
        notes_text = (
            f"R² = {r_squared:.3f} — empty cell count explains only a small share of the "
            f"variation in {target_label}. Puzzle difficulty depends on how constrained the "
            "empty cells are, not just how many there are, so this single-variable model is "
            "best read as illustrative rather than precise."
        )
    st.markdown(
        f'<div class="sil-notes">{notes_text} This is a simple one-variable linear fit on '
        "the currently filtered dataset, not a component of the C solver itself.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def page_research(full_df):
    # Page-scoped typography boost (slight, ~5%) — does not affect other pages.
    st.markdown(
        f"""
        <style>
            .sil-research h1 {{ font-size: 1.68rem; }}
            .sil-research h2, .sil-research h3 {{ font-size: 1.1rem; }}
            .sil-research .sil-section-label {{ font-size: 0.76rem; }}
            .sil-research .stCaption, .sil-research [data-testid="stCaptionContainer"] {{
                font-size: 0.89rem !important;
            }}
            .sil-research p, .sil-research li {{ font-size: 1.02rem; }}

            .sil-finding-card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 3px solid {ACCENT};
                border-radius: 8px;
                padding: 18px 20px;
                height: 100%;
            }}
            .sil-finding-card h4 {{
                margin: 0 0 10px 0;
                font-size: 0.98rem;
                font-weight: 600;
                color: {TEXT};
            }}
            .sil-finding-text {{
                margin: 4px 0 8px 0;
                font-size: 0.9rem;
                line-height: 1.5;
                color: {TEXT_MUTED};
            }}
            .sil-finding-text .label {{
                color: {TEXT};
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.7rem;
                letter-spacing: 0.05em;
                margin-right: 6px;
            }}
        </style>
        <div class="sil-research">
        """,
        unsafe_allow_html=True,
    )

    st.title("Research")
    st.caption("Executive summary of the Sudoku Intelligence Lab benchmark.")

    if full_df is None or full_df.empty:
        missing_results_notice()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    df = full_df

    # ---------------- Precompute statistics used throughout (display-only) ----------------
    corr_empty_calls = df["empty_cells"].corr(df["recursive_calls"]) if len(df) > 1 else float("nan")
    corr_calls_time = df["recursive_calls"].corr(df["execution_time_ms"]) if len(df) > 1 else float("nan")
    backtrack_ratio = (df["backtracks"] / df["recursive_calls"].replace(0, np.nan)).mean() * 100

    by_difficulty = df.groupby("difficulty")["execution_time_ms"].mean().reindex(DIFFICULTY_ORDER).dropna()
    if len(by_difficulty) >= 2:
        multiplier = by_difficulty.iloc[-1] / max(by_difficulty.iloc[0], 1e-9)
        multiplier_text = f"{multiplier:.1f}x"
    else:
        multiplier_text = "an unmeasured amount"

    # ============================================================
    # 1. Objective
    # ============================================================
    st.markdown('<div class="sil-section-label">1. Objective</div>', unsafe_allow_html=True)
    st.write(
        "This benchmark measures how a recursive backtracking Sudoku solver written "
        "in C behaves across puzzles of increasing difficulty. By instrumenting the "
        "solver to record recursive calls, backtracks, candidate checks, and "
        "execution time, the project aims to identify which internal metrics best "
        "explain solver cost, and how reliably puzzle difficulty predicts that cost."
    )

    st.divider()

    # ============================================================
    # 2. Methodology
    # ============================================================
    st.markdown('<div class="sil-section-label">2. Methodology</div>', unsafe_allow_html=True)
    _card_grid(
        [
            {
                "title": "Dataset",
                "desc": "1,000 Sudoku puzzles across four difficulty tiers (250 each), "
                "generated with a maintained puzzle library.",
            },
            {
                "title": "Solver",
                "desc": "A recursive backtracking solver written in C that assigns "
                "candidate values cell by cell until a valid completion is found.",
            },
            {
                "title": "Instrumentation",
                "desc": "Every solve records recursive calls, backtracks, candidate "
                "checks, and execution time, exported per puzzle to a results CSV.",
            },
            {
                "title": "Analysis Techniques",
                "desc": "Descriptive statistics, correlation analysis, and "
                "single-variable linear regression, computed in Python.",
            },
        ]
    )

    st.divider()

    # ============================================================
    # 3. Key Findings
    # ============================================================
    st.markdown('<div class="sil-section-label">3. Key Findings</div>', unsafe_allow_html=True)

    def finding_card(title, finding, evidence, implication):
        st.markdown(
            f'<div class="sil-finding-card"><h4>{title}</h4>'
            f'<p class="sil-finding-text"><span class="label">Finding</span>{finding}</p>'
            f'<p class="sil-finding-text"><span class="label">Evidence</span>{evidence}</p>'
            f'<p class="sil-finding-text"><span class="label">Implication</span>{implication}</p>'
            "</div>",
            unsafe_allow_html=True,
        )

    row1 = st.columns(2)
    with row1[0]:
        finding_card(
            "Difficulty tiers scale solver cost",
            "Harder difficulty tiers require substantially more search effort.",
            f"Average execution time increases roughly {multiplier_text} from the "
            "easiest to the hardest difficulty tier in the current dataset.",
            "Difficulty labels are a trustworthy stand-in for expected solver "
            "cost when planning benchmark runs.",
        )
    with row1[1]:
        recursive_corr_text = f"r = {corr_calls_time:.2f}" if not np.isnan(corr_calls_time) else "not available"
        finding_card(
            "Recursive calls predict execution time",
            "Execution time closely follows the number of recursive calls a "
            "puzzle requires.",
            f"Recursive calls and execution time correlate at {recursive_corr_text} "
            "(see Regression, Study 2).",
            "Recursive call count can substitute for wall-clock timing as a "
            "lower-noise cost metric in future benchmarking.",
        )

    row2 = st.columns(2)
    with row2[0]:
        finding_card(
            "Backtracking is a meaningful share of work",
            "The solver spends a non-trivial portion of its search undoing "
            "assignments.",
            f"On average, backtracks account for about {backtrack_ratio:.1f}% of "
            "recursive calls.",
            "Adding constraint propagation ahead of search could reduce wasted "
            "work and lower solve times.",
        )
    with row2[1]:
        empty_corr_text = f"r = {corr_empty_calls:.2f}" if not np.isnan(corr_empty_calls) else "not available"
        finding_card(
            "Empty cell count alone is a weak predictor",
            "The number of empty cells explains little of the variation in "
            "recursive calls on its own.",
            f"Empty cells and recursive calls correlate at only {empty_corr_text} "
            "(see Regression, Study 1).",
            "Difficulty estimation needs a structural signal beyond cell count, "
            "such as constraint density, not cell count alone.",
        )

    st.divider()

    # ============================================================
    # 4. Engineering Conclusions
    # ============================================================
    st.markdown('<div class="sil-section-label">4. Engineering Conclusions</div>', unsafe_allow_html=True)
    st.markdown(
        "- Recursive call count is the most dependable single metric for "
        "estimating solver cost, both for comparing puzzles and for predicting "
        "execution time.\n"
        "- Empty cell count alone is not a reliable difficulty proxy; puzzles "
        "with similar cell counts can require very different amounts of search.\n"
        "- The meaningful share of backtracking suggests that lightweight "
        "constraint propagation before search could reduce wasted recursive calls.\n"
        "- Because execution time tracks recursive calls closely, future "
        "profiling can lean on call counts to reduce noise from system-level "
        "timing variance."
    )

    st.divider()

    # ============================================================
    # 5. Future Work
    # ============================================================
    st.markdown('<div class="sil-section-label">5. Future Work</div>', unsafe_allow_html=True)
    _card_grid(
        [
            {
                "title": "Heuristic Solvers",
                "desc": "Add cell-ordering heuristics, such as minimum remaining "
                "values, to reduce backtracking before it happens.",
            },
            {
                "title": "Algorithm X (Dancing Links)",
                "desc": "Implement Knuth's Algorithm X as an exact-cover alternative "
                "and compare it against recursive backtracking.",
            },
            {
                "title": "Parallel Solving",
                "desc": "Explore parallelizing independent search branches to reduce "
                "wall-clock time on the hardest puzzles.",
            },
            {
                "title": "Broader CSP Benchmarking",
                "desc": "Extend the benchmark harness to other constraint "
                "satisfaction problems, such as N-Queens or graph coloring.",
            },
        ]
    )

    st.markdown("</div>", unsafe_allow_html=True)


def page_about():
    # Page-scoped typography boost (slight, ~5%) — does not affect other pages.
    st.markdown(
        f"""
        <style>
            .sil-about h1 {{ font-size: 1.68rem; }}
            .sil-about h2, .sil-about h3 {{ font-size: 1.1rem; }}
            .sil-about .sil-section-label {{ font-size: 0.76rem; }}
            .sil-about p, .sil-about li {{ font-size: 1.02rem; }}
            .sil-about div[data-testid="stMetricLabel"] {{ font-size: 0.82rem; }}
            .sil-about div[data-testid="stMetricValue"] {{ font-size: 1.58rem; }}
        </style>
        <div class="sil-about">
        """,
        unsafe_allow_html=True,
    )

    st.title("About")

    # ============================================================
    # 1. Project Overview
    # ============================================================
    st.markdown('<div class="sil-section-label">1. Project Overview</div>', unsafe_allow_html=True)
    st.write(
        "Sudoku Intelligence Lab benchmarks a recursive backtracking Sudoku solver "
        "written in C. Every solve is instrumented to record search behavior in "
        "detail, and the results are analyzed in this dashboard to understand what "
        "drives solver cost and how reliably it can be predicted."
    )

    st.divider()

    # ============================================================
    # 2. System Architecture
    # ============================================================
    st.markdown('<div class="sil-section-label">2. System Architecture</div>', unsafe_allow_html=True)
    st.markdown(
        _pipeline_diagram_svg(
            ["Dataset", "C Solver", "Performance Metrics", "CSV Results", "Python Analytics", "Dashboard"]
        ),
        unsafe_allow_html=True,
    )

    st.divider()

    # ============================================================
    # 3. Processing Pipeline
    # ============================================================
    st.markdown('<div class="sil-section-label">3. Processing Pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        "1. **Generate** a difficulty-balanced puzzle dataset (250 puzzles per tier).\n"
        "2. **Solve** every puzzle with the instrumented C backtracking solver.\n"
        "3. **Export** per-puzzle metrics and timing to a results CSV.\n"
        "4. **Analyze** the results in this dashboard: filtering, statistics, "
        "regression, and prediction."
    )

    st.divider()

    # ============================================================
    # 4. Technology Stack
    # ============================================================
    st.markdown('<div class="sil-section-label">4. Technology Stack</div>', unsafe_allow_html=True)
    tech_stack = pd.DataFrame(
        [
            {"Responsibility": "Solver", "Technology": "C"},
            {"Responsibility": "Dataset Generation", "Technology": "Python, dokusan"},
            {"Responsibility": "Analysis", "Technology": "NumPy, pandas"},
            {"Responsibility": "Dashboard", "Technology": "Streamlit, Plotly"},
        ]
    )
    st.dataframe(tech_stack, use_container_width=True, hide_index=True)

    st.divider()

    # ============================================================
    # 5. Repository Structure
    # ============================================================
    st.markdown('<div class="sil-section-label">5. Repository Structure</div>', unsafe_allow_html=True)
    st.code(
        "sudoku-intelligence-lab/\n"
        "├── solver.c / solver.h      # C solver + performance instrumentation\n"
        "├── dataset.c                # Benchmark harness, exports results.csv\n"
        "├── python/\n"
        "│   └── generate_dataset.py  # Puzzle dataset generation\n"
        "├── data/\n"
        "│   ├── dataset/             # Generated puzzle dataset (sudoku_dataset.csv)\n"
        "│   └── output/              # Benchmark results (results.csv)\n"
        "└── app.py                   # Streamlit dashboard",
        language="text",
    )

    st.divider()

    # ============================================================
    # 6. Project Statistics
    # ============================================================
    st.markdown('<div class="sil-section-label">6. Project Statistics</div>', unsafe_allow_html=True)
    stat_row1 = st.columns(3)
    stat_row1[0].metric("Benchmark Puzzles", "1,000")
    stat_row1[1].metric("Difficulty Tiers", "4")
    stat_row1[2].metric("Dashboard Pages", "7")

    stat_row2 = st.columns(3)
    stat_row2[0].metric("Recorded Metrics", "6")
    stat_row2[1].metric("Regression Studies", "2")
    stat_row2[2].metric("Solve Rate", "100%")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# App entry point
# =========================================================


def main():
    configure_page()

    st.sidebar.markdown(
        '<div style="font-weight:600; font-size:1rem; padding:4px 4px 12px 4px;">'
        "Sudoku Intelligence Lab</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="sil-nav-label">Navigation</div>', unsafe_allow_html=True)
    page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
    st.sidebar.divider()

    raw_results = load_results(RESULTS_PATH)
    results_df = prepare_results(raw_results)
    puzzles_df = load_puzzles(PUZZLES_PATH)

    filtered_df = results_df
    if page in ANALYTICS_PAGES and results_df is not None:
        filtered_df = render_sidebar_filters(results_df)

    if page == "Home":
        page_home(results_df, puzzles_df)
    elif page == "Explorer":
        page_explorer(results_df, puzzles_df)
    elif page == "Performance":
        page_performance(filtered_df)
    elif page == "Statistics":
        page_statistics(filtered_df)
    elif page == "Regression":
        page_regression(filtered_df)
    elif page == "Prediction":
        page_prediction(filtered_df)
    elif page == "Research":
        page_research(filtered_df)
    elif page == "About":
        page_about()


if __name__ == "__main__":
    main()
import csv
import random
from pathlib import Path


# ============================================================
# FROZEN CONFIRMATORY CONFIGURATION
# ============================================================

SEED = 20261003
SAMPLE_PER_STRATUM = 2500

ROOT = Path("research")

SOURCE_DIR = ROOT / "data" / "external" / "sudoku-exchange"

PILOT_PATH = (
    ROOT
    / "data"
    / "pilot"
    / "puzzles_100.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "confirmatory"
    / "puzzles_10000.csv"
)

SOURCE_FILES = {
    "easy": SOURCE_DIR / "easy.txt",
    "medium": SOURCE_DIR / "medium.txt",
    "hard": SOURCE_DIR / "hard.txt",
    "diabolical": SOURCE_DIR / "diabolical.txt",
}

ID_PREFIX = {
    "easy": "CE",
    "medium": "CM",
    "hard": "CH",
    "diabolical": "CD",
}


# ============================================================
# PUZZLE NORMALIZATION
# ============================================================

def canonicalize_puzzle(raw):
    """
    Convert a puzzle representation into a canonical
    81-character string containing digits 0-9.

    Supports:
    1. A standalone 81-character puzzle string.
    2. A Sudoku Exchange source record:
       <12-char hash> <81-char puzzle> <rating>

    '.' is converted to '0'.

    Returns None if malformed.
    """

    raw = raw.strip()

    if not raw:
        return None

    fields = raw.split()

    # Standalone puzzle representation
    if len(fields) == 1:
        token = fields[0]

    # Sudoku Exchange source format:
    # hash puzzle rating
    elif len(fields) >= 3:
        token = fields[1]

    else:
        return None

    token = token.strip().replace(".", "0")

    if len(token) != 81:
        return None

    if any(ch not in "0123456789" for ch in token):
        return None

    return token

# ============================================================
# INITIAL GRID VALIDATION
# ============================================================

def validate_initial_grid(puzzle):
    """
    Check that the given clues do not already violate
    row, column, or 3x3-box Sudoku constraints.

    This does NOT solve the puzzle.
    """

    grid = [
        [
            int(puzzle[r * 9 + c])
            for c in range(9)
        ]
        for r in range(9)
    ]

    def valid_group(values):
        nonzero = [
            value
            for value in values
            if value != 0
        ]

        return len(nonzero) == len(set(nonzero))

    # Rows
    for r in range(9):
        if not valid_group(grid[r]):
            return False

    # Columns
    for c in range(9):

        column = [
            grid[r][c]
            for r in range(9)
        ]

        if not valid_group(column):
            return False

    # 3x3 boxes
    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):

            box = []

            for r in range(box_r, box_r + 3):
                for c in range(box_c, box_c + 3):
                    box.append(grid[r][c])

            if not valid_group(box):
                return False

    return True


# ============================================================
# PILOT DATA
# ============================================================

def load_pilot_puzzles(path):
    """
    Load canonical puzzle strings from the exploratory
    100-puzzle pilot.

    Puzzle strings, rather than puzzle IDs, are used for
    contamination protection.
    """

    pilot = set()

    with path.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError(
                "Pilot CSV has no header."
            )

        if "puzzle" not in reader.fieldnames:
            raise ValueError(
                "Pilot CSV does not contain "
                "a 'puzzle' column."
            )

        for row_number, row in enumerate(
            reader,
            start=2
        ):

            puzzle = canonicalize_puzzle(
                row["puzzle"]
            )

            if puzzle is None:
                raise ValueError(
                    "Malformed pilot puzzle at "
                    f"CSV row {row_number}"
                )

            pilot.add(puzzle)

    return pilot


# ============================================================
# SOURCE LOADING
# ============================================================

def load_source_candidates(
    path,
    difficulty,
    pilot_puzzles
):
    """
    Read one Sudoku Exchange difficulty stratum.

    Each eligible puzzle retains its original source
    record number for provenance.

    Deduplication is based on canonical puzzle content.

    If a duplicate puzzle occurs more than once, the
    first eligible source occurrence is retained.
    """

    unique = {}

    total_records = 0
    malformed = 0
    invalid_grid = 0
    pilot_excluded = 0
    duplicates = 0

    with path.open(
        "r",
        encoding="utf-8"
    ) as f:

        for source_record_number, line in enumerate(
            f,
            start=1
        ):

            total_records += 1

            puzzle = canonicalize_puzzle(line)

            if puzzle is None:
                malformed += 1
                continue

            if not validate_initial_grid(puzzle):
                invalid_grid += 1
                continue

            if puzzle in pilot_puzzles:
                pilot_excluded += 1
                continue

            if puzzle in unique:
                duplicates += 1
                continue

            unique[puzzle] = {
                "puzzle": puzzle,
                "source_record_id": (
                    f"{difficulty}:"
                    f"{source_record_number}"
                ),
            }

    # Deterministic population ordering is important:
    # the seed alone is not enough if population order
    # changes between runs.
    candidates = [
        unique[puzzle]
        for puzzle in sorted(unique)
    ]

    audit = {
        "total_records": total_records,
        "malformed": malformed,
        "invalid_grid": invalid_grid,
        "pilot_excluded": pilot_excluded,
        "duplicates": duplicates,
        "valid_eligible": len(candidates),
    }

    return candidates, audit


# ============================================================
# DATASET CONSTRUCTION
# ============================================================

def main():

    print()
    print(
        "Build 5.3 - Confirmatory Dataset Builder"
    )
    print(
        "========================================"
    )
    print()

    # --------------------------------------------------------
    # Load exploratory pilot exclusion set
    # --------------------------------------------------------

    pilot_puzzles = load_pilot_puzzles(
        PILOT_PATH
    )

    if len(pilot_puzzles) != 100:
        raise RuntimeError(
            "Expected 100 unique pilot puzzles, "
            f"found {len(pilot_puzzles)}."
        )

    print("Frozen configuration")
    print("----------------------------------------")
    print(f"Seed               : {SEED}")
    print(
        f"Sample per stratum : "
        f"{SAMPLE_PER_STRATUM}"
    )
    print(
        f"Pilot puzzles      : "
        f"{len(pilot_puzzles)}"
    )
    print()

    # One deterministic RNG is used for the complete
    # stratified sampling procedure.
    rng = random.Random(SEED)

    selected_records = []

    global_selected = set()

    audits = {}

    difficulties = [
        "easy",
        "medium",
        "hard",
        "diabolical",
    ]

    # --------------------------------------------------------
    # Process each stratum
    # --------------------------------------------------------

    for difficulty in difficulties:

        candidates, audit = load_source_candidates(
            SOURCE_FILES[difficulty],
            difficulty,
            pilot_puzzles,
        )

        if len(candidates) < SAMPLE_PER_STRATUM:
            raise RuntimeError(
                "Not enough eligible puzzles in "
                f"{difficulty}: "
                f"{len(candidates)}"
            )

        sample = rng.sample(
            candidates,
            SAMPLE_PER_STRATUM,
        )

        # ----------------------------------------------------
        # Cross-stratum duplicate protection
        # ----------------------------------------------------

        sample_puzzles = {
            record["puzzle"]
            for record in sample
        }

        overlap = (
            sample_puzzles
            & global_selected
        )

        if overlap:
            raise RuntimeError(
                "Cross-stratum duplicate detected "
                f"in {difficulty}: "
                f"{len(overlap)} puzzle(s)"
            )

        global_selected.update(
            sample_puzzles
        )

        # ----------------------------------------------------
        # Generate deterministic confirmatory IDs
        # ----------------------------------------------------

        prefix = ID_PREFIX[difficulty]

        for index, record in enumerate(
            sample,
            start=1
        ):

            puzzle_id = (
                f"{prefix}{index:05d}"
            )

            selected_records.append(
                {
                    "puzzle_id": puzzle_id,
                    "puzzle": record["puzzle"],
                    "source": "sudoku_exchange",
                    "source_record_id":
                        record["source_record_id"],
                    "source_difficulty":
                        difficulty,
                    "sampling_seed": SEED,
                }
            )

        audits[difficulty] = audit

    # ========================================================
    # FINAL INTEGRITY CHECKS
    # ========================================================

    expected_total = (
        SAMPLE_PER_STRATUM
        * len(difficulties)
    )

    if len(selected_records) != expected_total:
        raise RuntimeError(
            "Unexpected confirmatory sample size: "
            f"{len(selected_records)}"
        )

    if len(global_selected) != expected_total:
        raise RuntimeError(
            "Confirmatory dataset contains "
            "duplicate puzzle strings."
        )

    pilot_overlap = (
        global_selected
        & pilot_puzzles
    )

    if pilot_overlap:
        raise RuntimeError(
            "Pilot contamination detected: "
            f"{len(pilot_overlap)} puzzle(s)"
        )

    puzzle_ids = [
        row["puzzle_id"]
        for row in selected_records
    ]

    if len(puzzle_ids) != len(set(puzzle_ids)):
        raise RuntimeError(
            "Duplicate confirmatory puzzle IDs detected."
        )

    source_ids = [
        row["source_record_id"]
        for row in selected_records
    ]

    if len(source_ids) != len(set(source_ids)):
        raise RuntimeError(
            "Duplicate source_record_id values detected."
        )

    # ========================================================
    # WRITE DATASET
    # ========================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "puzzle_id",
        "puzzle",
        "source",
        "source_record_id",
        "source_difficulty",
        "sampling_seed",
    ]

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(
            selected_records
        )

    # ========================================================
    # AUDIT REPORT
    # ========================================================

    print("Source audit")
    print("----------------------------------------")

    for difficulty in difficulties:

        a = audits[difficulty]

        print()
        print(difficulty.upper())

        print(
            f"  source records    : "
            f"{a['total_records']}"
        )

        print(
            f"  malformed         : "
            f"{a['malformed']}"
        )

        print(
            f"  invalid grids     : "
            f"{a['invalid_grid']}"
        )

        print(
            f"  pilot excluded    : "
            f"{a['pilot_excluded']}"
        )

        print(
            f"  source duplicates : "
            f"{a['duplicates']}"
        )

        print(
            f"  valid eligible    : "
            f"{a['valid_eligible']}"
        )

        print(
            f"  selected          : "
            f"{SAMPLE_PER_STRATUM}"
        )

    print()
    print("Final integrity")
    print("----------------------------------------")

    print(
        f"Selected records    : "
        f"{len(selected_records)}"
    )

    print(
        f"Unique puzzle IDs   : "
        f"{len(set(puzzle_ids))}"
    )

    print(
        f"Unique puzzles      : "
        f"{len(global_selected)}"
    )

    print(
        f"Unique source IDs   : "
        f"{len(set(source_ids))}"
    )

    print(
        f"Pilot overlap       : "
        f"{len(pilot_overlap)}"
    )

    print(
        "Cross-stratum dupes : 0"
    )

    print(
        f"Output              : "
        f"{OUTPUT_PATH}"
    )

    print()
    print("DATASET BUILD PASSED")


if __name__ == "__main__":
    main()
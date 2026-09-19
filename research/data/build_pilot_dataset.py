import csv
import random
from pathlib import Path


SOURCE_DIR = Path(
    "research/data/external/sudoku-exchange"
)

OUTPUT_FILE = Path(
    "research/data/pilot/puzzles_100.csv"
)

SEED = 2026
SAMPLES_PER_CLASS = 25

CLASSES = [
    "easy",
    "medium",
    "hard",
    "diabolical",
]


def extract_puzzle_from_line(line):
    """
    Find an 81-character Sudoku representation
    inside a source record.

    Accepts digits 0-9 and '.' for empty cells.
    """

    tokens = line.strip().split()

    for token in tokens:

        cleaned = token.strip()

        if (
            len(cleaned) == 81
            and all(ch in "0123456789." for ch in cleaned)
        ):
            return cleaned.replace(".", "0")

    return None


def load_category(category):
    """Load valid puzzle records from one source file."""

    path = SOURCE_DIR / f"{category}.txt"

    records = []

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        for line_number, line in enumerate(file, start=1):

            puzzle = extract_puzzle_from_line(line)

            if puzzle is None:
                continue

            records.append(
                {
                    "puzzle": puzzle,
                    "source_record_id":
                        f"{category}:{line_number}",
                }
            )

    return records


def validate_puzzle_string(puzzle):
    """Basic representation validation."""

    if len(puzzle) != 81:
        return False

    if not all(ch in "0123456789" for ch in puzzle):
        return False

    return True


def main():

    rng = random.Random(SEED)

    output_rows = []

    global_index = 1

    print("Building 100-puzzle pilot")
    print("-------------------------")

    for category in CLASSES:

        records = load_category(category)

        print(
            f"{category:10s}: "
            f"{len(records)} valid source records"
        )

        if len(records) < SAMPLES_PER_CLASS:
            raise RuntimeError(
                f"Not enough {category} puzzles."
            )

        selected = rng.sample(
            records,
            SAMPLES_PER_CLASS
        )

        for record in selected:

            puzzle = record["puzzle"]

            if not validate_puzzle_string(puzzle):
                raise RuntimeError(
                    "Invalid puzzle representation."
                )

            puzzle_id = f"SE{global_index:04d}"

            output_rows.append(
                {
                    "puzzle_id": puzzle_id,
                    "puzzle": puzzle,
                    "source": "sudoku_exchange",
                    "source_record_id":
                        record["source_record_id"],
                    "source_difficulty": category,
                    "sampling_seed": SEED,
                }
            )

            global_index += 1

    # Dataset-level checks
    assert len(output_rows) == 100

    puzzles = [
        row["puzzle"]
        for row in output_rows
    ]

    if len(set(puzzles)) != 100:
        raise RuntimeError(
            "Duplicate puzzles detected in pilot."
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "puzzle_id",
        "puzzle",
        "source",
        "source_record_id",
        "source_difficulty",
        "sampling_seed",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(output_rows)

    print()
    print("-------------------------")
    print("Pilot dataset created.")
    print(f"Puzzles: {len(output_rows)}")
    print(f"Seed:    {SEED}")
    print(f"Output:  {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
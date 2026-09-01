import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49 Dataset Validator
#
# Research window:
#   Draw 2995 - 4213
#   09 Oct 2014 - 31 Aug 2026
#
# Dataset:
#   1,219 draws
#
# Official frequency reference:
#   Singapore Pools
#   "Drawn Number Frequency"
#
# Snapshot corresponds to Draw 4213.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

EXPECTED_FIRST_DATE = "09 Oct 2014"
EXPECTED_LAST_DATE = "31 Aug 2026"

EXPECTED_MAIN_BALL_TOTAL = EXPECTED_ROWS * 6
EXPECTED_ADDITIONAL_TOTAL = EXPECTED_ROWS


# ------------------------------------------------------------
# Official Singapore Pools frequency snapshot
# through Draw 4213.
#
# key = ball number
# value = cumulative frequency
# ------------------------------------------------------------

OFFICIAL_MAIN_FREQUENCY = {
    1: 158,
    2: 153,
    3: 147,
    4: 152,
    5: 156,
    6: 148,
    7: 145,
    8: 159,
    9: 152,
    10: 155,
    11: 147,
    12: 158,
    13: 142,
    14: 140,
    15: 176,
    16: 142,
    17: 144,
    18: 139,
    19: 144,
    20: 145,
    21: 143,
    22: 165,
    23: 148,
    24: 151,
    25: 137,
    26: 143,
    27: 145,
    28: 163,
    29: 133,
    30: 156,
    31: 151,
    32: 159,
    33: 132,
    34: 149,
    35: 158,
    36: 155,
    37: 154,
    38: 146,
    39: 145,
    40: 172,
    41: 136,
    42: 128,
    43: 146,
    44: 157,
    45: 119,
    46: 166,
    47: 139,
    48: 154,
    49: 162,
}


OFFICIAL_ADDITIONAL_FREQUENCY = {
    1: 27,
    2: 27,
    3: 21,
    4: 17,
    5: 20,
    6: 33,
    7: 25,
    8: 28,
    9: 18,
    10: 25,
    11: 19,
    12: 25,
    13: 25,
    14: 20,
    15: 22,
    16: 28,
    17: 21,
    18: 29,
    19: 25,
    20: 37,
    21: 32,
    22: 22,
    23: 25,
    24: 25,
    25: 25,
    26: 20,
    27: 25,
    28: 22,
    29: 30,
    30: 26,
    31: 32,
    32: 14,
    33: 32,
    34: 30,
    35: 27,
    36: 27,
    37: 26,
    38: 18,
    39: 23,
    40: 18,
    41: 26,
    42: 28,
    43: 19,
    44: 29,
    45: 20,
    46: 25,
    47: 20,
    48: 33,
    49: 28,
}


def find_csv_file() -> Path:
    """
    Find the dataset depending on where this script is run.

    GitHub/repository structure:
        Special_01_Singapore_TOTO/
        ├── data/
        │   └── toto_draws_6of49.csv
        └── scripts/
            └── validate_results.py

    If this validator is downloaded directly into Downloads,
    it looks for the CSV in the same directory.
    """

    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    if script_dir.name.lower() == "scripts":
        candidate = (
            script_dir.parent
            / "data"
            / "toto_draws_6of49.csv"
        )
    else:
        candidate = (
            script_dir
            / "toto_draws_6of49.csv"
        )

    if not candidate.exists():
        raise FileNotFoundError(
            f"CSV file not found: {candidate}"
        )

    return candidate


def load_dataset(csv_file: Path) -> list[dict]:
    """
    Read the CSV and convert numeric fields to integers.
    """

    records = []

    with csv_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        expected_columns = [
            "draw_no",
            "draw_date",
            "n1",
            "n2",
            "n3",
            "n4",
            "n5",
            "n6",
            "additional",
        ]

        if reader.fieldnames != expected_columns:
            raise ValueError(
                "Unexpected CSV columns.\n"
                f"Expected: {expected_columns}\n"
                f"Found:    {reader.fieldnames}"
            )

        for row in reader:
            records.append(
                {
                    "draw_no": int(row["draw_no"]),
                    "draw_date": row["draw_date"],
                    "numbers": [
                        int(row["n1"]),
                        int(row["n2"]),
                        int(row["n3"]),
                        int(row["n4"]),
                        int(row["n5"]),
                        int(row["n6"]),
                    ],
                    "additional": int(
                        row["additional"]
                    ),
                }
            )

    return records


def validate_structure(
    records: list[dict],
) -> list[str]:
    """
    Validate the internal structure of every draw.
    """

    errors = []

    if len(records) != EXPECTED_ROWS:
        errors.append(
            f"Expected {EXPECTED_ROWS} rows, "
            f"found {len(records)}"
        )

    draw_numbers = [
        record["draw_no"]
        for record in records
    ]

    if len(draw_numbers) != len(set(draw_numbers)):
        errors.append(
            "Duplicate draw numbers detected."
        )

    expected_draw_numbers = set(
        range(FIRST_DRAW, LAST_DRAW + 1)
    )

    actual_draw_numbers = set(draw_numbers)

    missing_draws = sorted(
        expected_draw_numbers
        - actual_draw_numbers
    )

    extra_draws = sorted(
        actual_draw_numbers
        - expected_draw_numbers
    )

    if missing_draws:
        errors.append(
            "Missing draws: "
            + ", ".join(
                str(draw_no)
                for draw_no in missing_draws
            )
        )

    if extra_draws:
        errors.append(
            "Unexpected draws: "
            + ", ".join(
                str(draw_no)
                for draw_no in extra_draws
            )
        )

    for record in records:

        draw_no = record["draw_no"]
        numbers = record["numbers"]
        additional = record["additional"]

        if len(numbers) != 6:
            errors.append(
                f"Draw {draw_no}: "
                "does not have six main numbers."
            )

        if len(set(numbers)) != 6:
            errors.append(
                f"Draw {draw_no}: "
                "duplicate main number detected."
            )

        if numbers != sorted(numbers):
            errors.append(
                f"Draw {draw_no}: "
                "main numbers are not sorted."
            )

        for number in numbers:
            if not 1 <= number <= 49:
                errors.append(
                    f"Draw {draw_no}: "
                    f"invalid main number {number}."
                )

        if not 1 <= additional <= 49:
            errors.append(
                f"Draw {draw_no}: "
                f"invalid additional number "
                f"{additional}."
            )

        if additional in numbers:
            errors.append(
                f"Draw {draw_no}: "
                "additional number duplicates "
                "a main number."
            )

        try:
            datetime.strptime(
                record["draw_date"],
                "%d %b %Y",
            )
        except ValueError:
            errors.append(
                f"Draw {draw_no}: "
                f"invalid date format "
                f"{record['draw_date']}."
            )

    return errors


def validate_endpoints(
    records: list[dict],
) -> list[str]:
    """
    Check the first and last records.
    """

    errors = []

    ordered = sorted(
        records,
        key=lambda record: record["draw_no"],
    )

    first = ordered[0]
    last = ordered[-1]

    if first["draw_no"] != FIRST_DRAW:
        errors.append(
            f"First draw should be {FIRST_DRAW}, "
            f"found {first['draw_no']}."
        )

    if first["draw_date"] != EXPECTED_FIRST_DATE:
        errors.append(
            f"First date should be "
            f"{EXPECTED_FIRST_DATE}, "
            f"found {first['draw_date']}."
        )

    if last["draw_no"] != LAST_DRAW:
        errors.append(
            f"Last draw should be {LAST_DRAW}, "
            f"found {last['draw_no']}."
        )

    if last["draw_date"] != EXPECTED_LAST_DATE:
        errors.append(
            f"Last date should be "
            f"{EXPECTED_LAST_DATE}, "
            f"found {last['draw_date']}."
        )

    return errors


def calculate_frequencies(
    records: list[dict],
) -> tuple[Counter, Counter]:

    main_counter = Counter()
    additional_counter = Counter()

    for record in records:

        main_counter.update(
            record["numbers"]
        )

        additional_counter.update(
            [record["additional"]]
        )

    return (
        main_counter,
        additional_counter,
    )


def compare_with_official(
    calculated: Counter,
    official: dict[int, int],
    label: str,
) -> list[str]:
    """
    Compare all 49 calculated frequencies
    against the official Singapore Pools snapshot.
    """

    errors = []

    print()
    print(label)
    print("-" * 60)
    print(
        f"{'Ball':>4} "
        f"{'Calculated':>12} "
        f"{'Official':>10} "
        f"{'Result':>10}"
    )

    for ball in range(1, 50):

        calculated_value = calculated[ball]
        official_value = official[ball]

        if calculated_value == official_value:
            result = "OK"
        else:
            result = "MISMATCH"

            errors.append(
                f"Ball {ball}: "
                f"calculated={calculated_value}, "
                f"official={official_value}"
            )

        print(
            f"{ball:>4} "
            f"{calculated_value:>12} "
            f"{official_value:>10} "
            f"{result:>10}"
        )

    return errors


def main() -> None:

    print()
    print("=" * 60)
    print("Singapore TOTO 6/49 Dataset Validation")
    print("=" * 60)

    csv_file = find_csv_file()

    print(f"Dataset: {csv_file}")

    records = load_dataset(csv_file)

    print(f"Rows loaded: {len(records)}")

    all_errors = []

    # --------------------------------------------------------
    # Structural checks
    # --------------------------------------------------------

    structure_errors = validate_structure(
        records
    )

    endpoint_errors = validate_endpoints(
        records
    )

    all_errors.extend(structure_errors)
    all_errors.extend(endpoint_errors)

    # --------------------------------------------------------
    # Frequency calculation
    # --------------------------------------------------------

    (
        main_frequency,
        additional_frequency,
    ) = calculate_frequencies(records)

    calculated_main_total = sum(
        main_frequency.values()
    )

    calculated_additional_total = sum(
        additional_frequency.values()
    )

    print()
    print("=" * 60)
    print("TOTAL FREQUENCY CHECK")
    print("=" * 60)

    print(
        f"Main balls expected : "
        f"{EXPECTED_MAIN_BALL_TOTAL}"
    )

    print(
        f"Main balls counted  : "
        f"{calculated_main_total}"
    )

    print(
        f"Additional expected : "
        f"{EXPECTED_ADDITIONAL_TOTAL}"
    )

    print(
        f"Additional counted  : "
        f"{calculated_additional_total}"
    )

    if (
        calculated_main_total
        != EXPECTED_MAIN_BALL_TOTAL
    ):
        all_errors.append(
            "Main-ball total frequency mismatch."
        )

    if (
        calculated_additional_total
        != EXPECTED_ADDITIONAL_TOTAL
    ):
        all_errors.append(
            "Additional-number total "
            "frequency mismatch."
        )

    # --------------------------------------------------------
    # Official frequency comparison
    # --------------------------------------------------------

    main_frequency_errors = (
        compare_with_official(
            main_frequency,
            OFFICIAL_MAIN_FREQUENCY,
            "MAIN BALL FREQUENCY",
        )
    )

    additional_frequency_errors = (
        compare_with_official(
            additional_frequency,
            OFFICIAL_ADDITIONAL_FREQUENCY,
            "ADDITIONAL NUMBER FREQUENCY",
        )
    )

    all_errors.extend(
        main_frequency_errors
    )

    all_errors.extend(
        additional_frequency_errors
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FINAL VALIDATION RESULT")
    print("=" * 60)

    if not all_errors:

        print(
            "[PASS] Dataset matches the official "
            "Singapore Pools frequency snapshot."
        )

        print()
        print(
            "Validated draws : "
            f"{FIRST_DRAW} - {LAST_DRAW}"
        )

        print(
            "Validated rows  : "
            f"{EXPECTED_ROWS}"
        )

        print(
            "Main frequencies matched       : 49/49"
        )

        print(
            "Additional frequencies matched : 49/49"
        )

    else:

        print(
            "[FAIL] Validation errors detected."
        )

        print()

        for error in all_errors:
            print(f"- {error}")

    print("=" * 60)


if __name__ == "__main__":
    main()

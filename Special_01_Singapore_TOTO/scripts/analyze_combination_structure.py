import csv
import random
import statistics
from collections import Counter
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49 Combination Structure Analysis
#
# Purpose:
#   Compare structural characteristics of real historical
#   TOTO winning combinations with uniformly random 6/49
#   combinations.
#
# Features:
#   - Sum of six numbers
#   - Odd / even composition
#   - Low / high composition
#   - Consecutive numbers
#   - Gap statistics
#   - Range
#   - Previous-draw overlap
#
# Important:
#   This script tests whether the SHAPE of historical winning
#   combinations differs from what would be expected under
#   random 6-from-49 sampling.
#
# It does NOT assume that any detected difference is
# exploitable for future prediction.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

BALL_MIN = 1
BALL_MAX = 49
PICKS_PER_TICKET = 6

RANDOM_SEED = 20260902

# Use many more random combinations than historical draws
# to obtain a stable reference distribution.
RANDOM_REFERENCE_RUNS = 1_000_000


def get_project_paths():
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    if script_dir.name.lower() == "scripts":
        project_dir = script_dir.parent

        csv_file = (
            project_dir
            / "data"
            / "toto_draws_6of49.csv"
        )

        results_dir = (
            project_dir
            / "results"
        )

    else:
        csv_file = (
            script_dir
            / "toto_draws_6of49.csv"
        )

        results_dir = (
            script_dir
            / "results"
        )

    if not csv_file.exists():
        raise FileNotFoundError(
            f"Dataset not found: {csv_file}"
        )

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return csv_file, results_dir


def load_dataset(csv_file):
    records = []

    with csv_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            numbers = sorted(
                [
                    int(row["n1"]),
                    int(row["n2"]),
                    int(row["n3"]),
                    int(row["n4"]),
                    int(row["n5"]),
                    int(row["n6"]),
                ]
            )

            records.append(
                {
                    "draw_no": int(
                        row["draw_no"]
                    ),
                    "draw_date": row[
                        "draw_date"
                    ],
                    "numbers": numbers,
                }
            )

    records.sort(
        key=lambda record:
        record["draw_no"]
    )

    if len(records) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} draws, "
            f"found {len(records)}"
        )

    if records[0]["draw_no"] != FIRST_DRAW:
        raise ValueError(
            f"Unexpected first draw: "
            f"{records[0]['draw_no']}"
        )

    if records[-1]["draw_no"] != LAST_DRAW:
        raise ValueError(
            f"Unexpected last draw: "
            f"{records[-1]['draw_no']}"
        )

    return records


def make_random_ticket(rng):
    return sorted(
        rng.sample(
            range(
                BALL_MIN,
                BALL_MAX + 1,
            ),
            PICKS_PER_TICKET,
        )
    )


def calculate_sum(numbers):
    return sum(numbers)


def calculate_odd_count(numbers):
    return sum(
        1
        for number in numbers
        if number % 2 == 1
    )


def calculate_low_count(numbers):
    """
    Low:
        1 - 24

    High:
        25 - 49
    """
    return sum(
        1
        for number in numbers
        if number <= 24
    )


def contains_consecutive(numbers):
    for left, right in zip(
        numbers,
        numbers[1:],
    ):
        if right - left == 1:
            return True

    return False


def count_consecutive_pairs(numbers):
    count = 0

    for left, right in zip(
        numbers,
        numbers[1:],
    ):
        if right - left == 1:
            count += 1

    return count


def calculate_gaps(numbers):
    return [
        right - left
        for left, right in zip(
            numbers,
            numbers[1:],
        )
    ]


def calculate_range(numbers):
    return (
        max(numbers)
        - min(numbers)
    )


def calculate_features(numbers):
    gaps = calculate_gaps(
        numbers
    )

    return {
        "sum":
            calculate_sum(
                numbers
            ),

        "odd_count":
            calculate_odd_count(
                numbers
            ),

        "low_count":
            calculate_low_count(
                numbers
            ),

        "has_consecutive":
            contains_consecutive(
                numbers
            ),

        "consecutive_pairs":
            count_consecutive_pairs(
                numbers
            ),

        "mean_gap":
            statistics.mean(
                gaps
            ),

        "min_gap":
            min(gaps),

        "max_gap":
            max(gaps),

        "range":
            calculate_range(
                numbers
            ),

        "minimum":
            min(numbers),

        "maximum":
            max(numbers),
    }


def calculate_real_features(records):
    rows = []

    previous_numbers = None

    for record in records:
        numbers = (
            record["numbers"]
        )

        features = (
            calculate_features(
                numbers
            )
        )

        if previous_numbers is None:
            overlap = None
        else:
            overlap = len(
                set(numbers)
                & set(previous_numbers)
            )

        row = {
            "draw_no":
                record["draw_no"],

            "draw_date":
                record["draw_date"],

            "numbers":
                "-".join(
                    str(number)
                    for number in numbers
                ),

            "sum":
                features["sum"],

            "odd_count":
                features["odd_count"],

            "even_count":
                PICKS_PER_TICKET
                - features["odd_count"],

            "low_count":
                features["low_count"],

            "high_count":
                PICKS_PER_TICKET
                - features["low_count"],

            "has_consecutive":
                int(
                    features[
                        "has_consecutive"
                    ]
                ),

            "consecutive_pairs":
                features[
                    "consecutive_pairs"
                ],

            "mean_gap":
                features[
                    "mean_gap"
                ],

            "min_gap":
                features[
                    "min_gap"
                ],

            "max_gap":
                features[
                    "max_gap"
                ],

            "range":
                features[
                    "range"
                ],

            "minimum":
                features[
                    "minimum"
                ],

            "maximum":
                features[
                    "maximum"
                ],

            "previous_draw_overlap":
                overlap,
        }

        rows.append(row)

        previous_numbers = (
            numbers
        )

    return rows


def generate_random_reference():
    rng = random.Random(
        RANDOM_SEED
    )

    sums = []
    odd_counts = Counter()
    low_counts = Counter()

    consecutive_count = 0
    consecutive_pair_counts = Counter()

    mean_gaps = []
    min_gaps = []
    max_gaps = []
    ranges = []
    minimums = []
    maximums = []

    previous_ticket = None
    overlap_counts = Counter()

    progress_interval = (
        RANDOM_REFERENCE_RUNS
        // 10
    )

    for run_no in range(
        1,
        RANDOM_REFERENCE_RUNS + 1,
    ):

        ticket = (
            make_random_ticket(
                rng
            )
        )

        features = (
            calculate_features(
                ticket
            )
        )

        sums.append(
            features["sum"]
        )

        odd_counts[
            features["odd_count"]
        ] += 1

        low_counts[
            features["low_count"]
        ] += 1

        if features[
            "has_consecutive"
        ]:
            consecutive_count += 1

        consecutive_pair_counts[
            features[
                "consecutive_pairs"
            ]
        ] += 1

        mean_gaps.append(
            features["mean_gap"]
        )

        min_gaps.append(
            features["min_gap"]
        )

        max_gaps.append(
            features["max_gap"]
        )

        ranges.append(
            features["range"]
        )

        minimums.append(
            features["minimum"]
        )

        maximums.append(
            features["maximum"]
        )

        if previous_ticket is not None:
            overlap = len(
                set(ticket)
                & set(previous_ticket)
            )

            overlap_counts[
                overlap
            ] += 1

        previous_ticket = (
            ticket
        )

        if (
            progress_interval > 0
            and run_no
            % progress_interval == 0
        ):
            print(
                f"[PROGRESS] "
                f"{run_no:,} "
                f"/ "
                f"{RANDOM_REFERENCE_RUNS:,}"
            )

    return {
        "sums": sums,
        "odd_counts": odd_counts,
        "low_counts": low_counts,
        "consecutive_count":
            consecutive_count,
        "consecutive_pair_counts":
            consecutive_pair_counts,
        "mean_gaps": mean_gaps,
        "min_gaps": min_gaps,
        "max_gaps": max_gaps,
        "ranges": ranges,
        "minimums": minimums,
        "maximums": maximums,
        "overlap_counts":
            overlap_counts,
    }


def summarize_real(rows):
    valid_overlap_rows = [
        row
        for row in rows
        if row[
            "previous_draw_overlap"
        ] is not None
    ]

    return {
        "count":
            len(rows),

        "sum_mean":
            statistics.mean(
                row["sum"]
                for row in rows
            ),

        "sum_median":
            statistics.median(
                row["sum"]
                for row in rows
            ),

        "sum_stdev":
            statistics.stdev(
                row["sum"]
                for row in rows
            ),

        "odd_distribution":
            Counter(
                row["odd_count"]
                for row in rows
            ),

        "low_distribution":
            Counter(
                row["low_count"]
                for row in rows
            ),

        "consecutive_count":
            sum(
                row["has_consecutive"]
                for row in rows
            ),

        "consecutive_pair_distribution":
            Counter(
                row[
                    "consecutive_pairs"
                ]
                for row in rows
            ),

        "mean_gap_mean":
            statistics.mean(
                row["mean_gap"]
                for row in rows
            ),

        "min_gap_mean":
            statistics.mean(
                row["min_gap"]
                for row in rows
            ),

        "max_gap_mean":
            statistics.mean(
                row["max_gap"]
                for row in rows
            ),

        "range_mean":
            statistics.mean(
                row["range"]
                for row in rows
            ),

        "minimum_mean":
            statistics.mean(
                row["minimum"]
                for row in rows
            ),

        "maximum_mean":
            statistics.mean(
                row["maximum"]
                for row in rows
            ),

        "overlap_distribution":
            Counter(
                row[
                    "previous_draw_overlap"
                ]
                for row
                in valid_overlap_rows
            ),
    }


def summarize_random(reference):
    return {
        "count":
            RANDOM_REFERENCE_RUNS,

        "sum_mean":
            statistics.mean(
                reference["sums"]
            ),

        "sum_median":
            statistics.median(
                reference["sums"]
            ),

        "sum_stdev":
            statistics.stdev(
                reference["sums"]
            ),

        "odd_distribution":
            reference[
                "odd_counts"
            ],

        "low_distribution":
            reference[
                "low_counts"
            ],

        "consecutive_count":
            reference[
                "consecutive_count"
            ],

        "consecutive_pair_distribution":
            reference[
                "consecutive_pair_counts"
            ],

        "mean_gap_mean":
            statistics.mean(
                reference[
                    "mean_gaps"
                ]
            ),

        "min_gap_mean":
            statistics.mean(
                reference[
                    "min_gaps"
                ]
            ),

        "max_gap_mean":
            statistics.mean(
                reference[
                    "max_gaps"
                ]
            ),

        "range_mean":
            statistics.mean(
                reference[
                    "ranges"
                ]
            ),

        "minimum_mean":
            statistics.mean(
                reference[
                    "minimums"
                ]
            ),

        "maximum_mean":
            statistics.mean(
                reference[
                    "maximums"
                ]
            ),

        "overlap_distribution":
            reference[
                "overlap_counts"
            ],
    }


def percentage(
    numerator,
    denominator,
):
    if denominator == 0:
        return 0.0

    return (
        numerator
        / denominator
        * 100
    )


def save_real_detail(
    rows,
    output_file,
):
    fieldnames = [
        "draw_no",
        "draw_date",
        "numbers",
        "sum",
        "odd_count",
        "even_count",
        "low_count",
        "high_count",
        "has_consecutive",
        "consecutive_pairs",
        "mean_gap",
        "min_gap",
        "max_gap",
        "range",
        "minimum",
        "maximum",
        "previous_draw_overlap",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


def save_comparison_csv(
    real_summary,
    random_summary,
    output_file,
):
    rows = []

    rows.append(
        {
            "metric":
                "sum_mean",
            "real":
                real_summary[
                    "sum_mean"
                ],
            "random":
                random_summary[
                    "sum_mean"
                ],
            "difference":
                real_summary[
                    "sum_mean"
                ]
                - random_summary[
                    "sum_mean"
                ],
        }
    )

    rows.append(
        {
            "metric":
                "sum_stdev",
            "real":
                real_summary[
                    "sum_stdev"
                ],
            "random":
                random_summary[
                    "sum_stdev"
                ],
            "difference":
                real_summary[
                    "sum_stdev"
                ]
                - random_summary[
                    "sum_stdev"
                ],
        }
    )

    rows.append(
        {
            "metric":
                "mean_gap_mean",
            "real":
                real_summary[
                    "mean_gap_mean"
                ],
            "random":
                random_summary[
                    "mean_gap_mean"
                ],
            "difference":
                real_summary[
                    "mean_gap_mean"
                ]
                - random_summary[
                    "mean_gap_mean"
                ],
        }
    )

    rows.append(
        {
            "metric":
                "min_gap_mean",
            "real":
                real_summary[
                    "min_gap_mean"
                ],
            "random":
                random_summary[
                    "min_gap_mean"
                ],
            "difference":
                real_summary[
                    "min_gap_mean"
                ]
                - random_summary[
                    "min_gap_mean"
                ],
        }
    )

    rows.append(
        {
            "metric":
                "max_gap_mean",
            "real":
                real_summary[
                    "max_gap_mean"
                ],
            "random":
                random_summary[
                    "max_gap_mean"
                ],
            "difference":
                real_summary[
                    "max_gap_mean"
                ]
                - random_summary[
                    "max_gap_mean"
                ],
        }
    )

    rows.append(
        {
            "metric":
                "range_mean",
            "real":
                real_summary[
                    "range_mean"
                ],
            "random":
                random_summary[
                    "range_mean"
                ],
            "difference":
                real_summary[
                    "range_mean"
                ]
                - random_summary[
                    "range_mean"
                ],
        }
    )

    rows.append(
        {
            "metric":
                "minimum_mean",
            "real":
                real_summary[
                    "minimum_mean"
                ],
            "random":
                random_summary[
                    "minimum_mean"
                ],
            "difference":
                real_summary[
                    "minimum_mean"
                ]
                - random_summary[
                    "minimum_mean"
                ],
        }
    )

    rows.append(
        {
            "metric":
                "maximum_mean",
            "real":
                real_summary[
                    "maximum_mean"
                ],
            "random":
                random_summary[
                    "maximum_mean"
                ],
            "difference":
                real_summary[
                    "maximum_mean"
                ]
                - random_summary[
                    "maximum_mean"
                ],
        }
    )

    real_consecutive_rate = (
        percentage(
            real_summary[
                "consecutive_count"
            ],
            real_summary[
                "count"
            ],
        )
    )

    random_consecutive_rate = (
        percentage(
            random_summary[
                "consecutive_count"
            ],
            random_summary[
                "count"
            ],
        )
    )

    rows.append(
        {
            "metric":
                "consecutive_draw_rate_percent",
            "real":
                real_consecutive_rate,
            "random":
                random_consecutive_rate,
            "difference":
                real_consecutive_rate
                - random_consecutive_rate,
        }
    )

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "metric",
                "real",
                "random",
                "difference",
            ],
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


def save_summary(
    real_summary,
    random_summary,
    output_file,
):
    real_count = (
        real_summary[
            "count"
        ]
    )

    random_count = (
        random_summary[
            "count"
        ]
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Singapore TOTO 6/49 "
            "Combination Structure Analysis\n"
        )

        file.write(
            "=" * 70
            + "\n\n"
        )

        file.write(
            f"Historical draws : "
            f"{real_count}\n"
        )

        file.write(
            f"Random reference : "
            f"{random_count:,}\n\n"
        )

        file.write(
            "CONTINUOUS FEATURES\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        comparisons = [
            (
                "Sum mean",
                "sum_mean",
            ),
            (
                "Sum stdev",
                "sum_stdev",
            ),
            (
                "Mean gap",
                "mean_gap_mean",
            ),
            (
                "Min gap",
                "min_gap_mean",
            ),
            (
                "Max gap",
                "max_gap_mean",
            ),
            (
                "Range",
                "range_mean",
            ),
            (
                "Minimum",
                "minimum_mean",
            ),
            (
                "Maximum",
                "maximum_mean",
            ),
        ]

        for label, key in comparisons:
            real_value = (
                real_summary[
                    key
                ]
            )

            random_value = (
                random_summary[
                    key
                ]
            )

            difference = (
                real_value
                - random_value
            )

            file.write(
                f"{label:<12} "
                f"Real={real_value:.6f} "
                f"Random={random_value:.6f} "
                f"Diff={difference:+.6f}\n"
            )

        file.write("\n")

        real_consecutive_rate = (
            percentage(
                real_summary[
                    "consecutive_count"
                ],
                real_count,
            )
        )

        random_consecutive_rate = (
            percentage(
                random_summary[
                    "consecutive_count"
                ],
                random_count,
            )
        )

        file.write(
            "CONSECUTIVE NUMBERS\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        file.write(
            "Historical rate : "
            f"{real_consecutive_rate:.4f}%\n"
        )

        file.write(
            "Random rate     : "
            f"{random_consecutive_rate:.4f}%\n"
        )

        file.write(
            "Difference      : "
            f"{real_consecutive_rate - random_consecutive_rate:+.4f} "
            "percentage points\n\n"
        )

        file.write(
            "ODD / EVEN DISTRIBUTION\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        for odd_count in range(
            0,
            PICKS_PER_TICKET + 1,
        ):
            real_value = (
                real_summary[
                    "odd_distribution"
                ][odd_count]
            )

            random_value = (
                random_summary[
                    "odd_distribution"
                ][odd_count]
            )

            file.write(
                f"{odd_count} odd / "
                f"{PICKS_PER_TICKET - odd_count} even  "
                f"Real={percentage(real_value, real_count):.4f}%  "
                f"Random={percentage(random_value, random_count):.4f}%\n"
            )

        file.write("\n")

        file.write(
            "LOW / HIGH DISTRIBUTION\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        for low_count in range(
            0,
            PICKS_PER_TICKET + 1,
        ):
            real_value = (
                real_summary[
                    "low_distribution"
                ][low_count]
            )

            random_value = (
                random_summary[
                    "low_distribution"
                ][low_count]
            )

            file.write(
                f"{low_count} low / "
                f"{PICKS_PER_TICKET - low_count} high  "
                f"Real={percentage(real_value, real_count):.4f}%  "
                f"Random={percentage(random_value, random_count):.4f}%\n"
            )

        file.write("\n")

        file.write(
            "PREVIOUS-DRAW OVERLAP\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        real_overlap_total = (
            real_count - 1
        )

        random_overlap_total = sum(
            random_summary[
                "overlap_distribution"
            ].values()
        )

        for overlap in range(
            0,
            PICKS_PER_TICKET + 1,
        ):
            real_value = (
                real_summary[
                    "overlap_distribution"
                ][overlap]
            )

            random_value = (
                random_summary[
                    "overlap_distribution"
                ][overlap]
            )

            file.write(
                f"{overlap} repeated numbers  "
                f"Real={percentage(real_value, real_overlap_total):.4f}%  "
                f"Random={percentage(random_value, random_overlap_total):.4f}%\n"
            )

        file.write("\n")

        file.write(
            "INTERPRETATION NOTE\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        file.write(
            "Small differences are expected because the historical "
            "sample contains only 1,219 draws.\n"
        )

        file.write(
            "A meaningful structural signal would require differences "
            "large enough to persist across independent periods and "
            "future draws.\n"
        )


def print_summary(
    real_summary,
    random_summary,
):
    print()
    print("=" * 78)

    print(
        "COMBINATION STRUCTURE COMPARISON"
    )

    print("=" * 78)

    print(
        f"Historical draws : "
        f"{real_summary['count']}"
    )

    print(
        f"Random reference : "
        f"{random_summary['count']:,}"
    )

    print()

    comparisons = [
        (
            "Sum mean",
            "sum_mean",
        ),
        (
            "Sum stdev",
            "sum_stdev",
        ),
        (
            "Mean gap",
            "mean_gap_mean",
        ),
        (
            "Min gap",
            "min_gap_mean",
        ),
        (
            "Max gap",
            "max_gap_mean",
        ),
        (
            "Range",
            "range_mean",
        ),
        (
            "Minimum",
            "minimum_mean",
        ),
        (
            "Maximum",
            "maximum_mean",
        ),
    ]

    print(
        f"{'Metric':<14} "
        f"{'Real':>12} "
        f"{'Random':>12} "
        f"{'Diff':>12}"
    )

    print("-" * 78)

    for label, key in comparisons:
        real_value = (
            real_summary[
                key
            ]
        )

        random_value = (
            random_summary[
                key
            ]
        )

        difference = (
            real_value
            - random_value
        )

        print(
            f"{label:<14} "
            f"{real_value:>12.6f} "
            f"{random_value:>12.6f} "
            f"{difference:>+12.6f}"
        )

    real_consecutive_rate = (
        percentage(
            real_summary[
                "consecutive_count"
            ],
            real_summary[
                "count"
            ],
        )
    )

    random_consecutive_rate = (
        percentage(
            random_summary[
                "consecutive_count"
            ],
            random_summary[
                "count"
            ],
        )
    )

    print()
    print(
        "Consecutive-number draw rate"
    )

    print(
        f"Real   : "
        f"{real_consecutive_rate:.4f}%"
    )

    print(
        f"Random : "
        f"{random_consecutive_rate:.4f}%"
    )

    print(
        f"Diff   : "
        f"{real_consecutive_rate - random_consecutive_rate:+.4f} pp"
    )


def main():
    (
        csv_file,
        results_dir,
    ) = get_project_paths()

    print()
    print("=" * 70)

    print(
        "Singapore TOTO 6/49 "
        "Combination Structure Analysis"
    )

    print("=" * 70)

    print(
        f"Dataset: {csv_file}"
    )

    records = load_dataset(
        csv_file
    )

    print(
        f"Historical draws loaded: "
        f"{len(records)}"
    )

    print()
    print(
        "[START] Calculating historical structure..."
    )

    real_rows = (
        calculate_real_features(
            records
        )
    )

    real_summary = (
        summarize_real(
            real_rows
        )
    )

    print(
        "[START] Generating "
        f"{RANDOM_REFERENCE_RUNS:,} "
        "random reference combinations..."
    )

    random_reference = (
        generate_random_reference()
    )

    random_summary = (
        summarize_random(
            random_reference
        )
    )

    detail_file = (
        results_dir
        / "combination_structure_historical.csv"
    )

    comparison_file = (
        results_dir
        / "combination_structure_comparison.csv"
    )

    summary_file = (
        results_dir
        / "combination_structure_summary.txt"
    )

    save_real_detail(
        real_rows,
        detail_file,
    )

    save_comparison_csv(
        real_summary,
        random_summary,
        comparison_file,
    )

    save_summary(
        real_summary,
        random_summary,
        summary_file,
    )

    print_summary(
        real_summary,
        random_summary,
    )

    print()
    print("=" * 70)

    print(
        "OUTPUT FILES"
    )

    print("=" * 70)

    print(
        f"[FILE] {detail_file}"
    )

    print(
        f"[FILE] {comparison_file}"
    )

    print(
        f"[FILE] {summary_file}"
    )

    print()
    print(
        "[DONE] Combination structure analysis complete."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()

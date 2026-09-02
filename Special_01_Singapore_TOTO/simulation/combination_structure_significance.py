import csv
import math
import random
import statistics
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49
# Combination Structure Significance Test
#
# Purpose:
#   Test whether observed structural differences between
#   historical TOTO draws and random 6/49 combinations are
#   statistically unusual.
#
# Tested features:
#   - Sum of six numbers
#   - Mean gap
#   - Minimum gap
#   - Maximum gap
#   - Range
#   - Minimum number
#   - Maximum number
#   - Consecutive-number draw rate
#
# Method:
#   Historical sample:
#       Draw 2995 - 4213
#
#   Null reference:
#       Uniform random 6-from-49 draws
#
#   Tests:
#       - Monte Carlo sampling distribution
#       - Two-sided empirical p-values
#       - Multiple-testing correction
#
# Important:
#   This script is designed to test whether apparent
#   structural differences are compatible with randomness.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

BALL_MIN = 1
BALL_MAX = 49
PICKS_PER_TICKET = 6

MONTE_CARLO_EXPERIMENTS = 10000
RANDOM_SEED = 20260902

ALPHA = 0.05


def get_project_paths():
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    if script_dir.name.lower() == "simulation":
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
            f"Expected {EXPECTED_ROWS} rows, "
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


def calculate_gaps(numbers):
    return [
        right - left
        for left, right in zip(
            numbers,
            numbers[1:],
        )
    ]


def has_consecutive(numbers):
    return any(
        right - left == 1
        for left, right in zip(
            numbers,
            numbers[1:],
        )
    )


def calculate_sample_metrics(
    tickets,
):
    sums = []

    mean_gaps = []
    min_gaps = []
    max_gaps = []

    ranges = []
    minimums = []
    maximums = []

    consecutive_count = 0

    for numbers in tickets:
        gaps = calculate_gaps(
            numbers
        )

        sums.append(
            sum(numbers)
        )

        mean_gaps.append(
            statistics.mean(
                gaps
            )
        )

        min_gaps.append(
            min(gaps)
        )

        max_gaps.append(
            max(gaps)
        )

        ranges.append(
            max(numbers)
            - min(numbers)
        )

        minimums.append(
            min(numbers)
        )

        maximums.append(
            max(numbers)
        )

        if has_consecutive(
            numbers
        ):
            consecutive_count += 1

    count = len(tickets)

    return {
        "sum_mean":
            statistics.mean(
                sums
            ),

        "mean_gap_mean":
            statistics.mean(
                mean_gaps
            ),

        "min_gap_mean":
            statistics.mean(
                min_gaps
            ),

        "max_gap_mean":
            statistics.mean(
                max_gaps
            ),

        "range_mean":
            statistics.mean(
                ranges
            ),

        "minimum_mean":
            statistics.mean(
                minimums
            ),

        "maximum_mean":
            statistics.mean(
                maximums
            ),

        "consecutive_rate":
            consecutive_count
            / count,
    }


def get_historical_metrics(
    records,
):
    tickets = [
        record["numbers"]
        for record in records
    ]

    return calculate_sample_metrics(
        tickets
    )


def generate_null_distributions():
    rng = random.Random(
        RANDOM_SEED
    )

    metric_names = [
        "sum_mean",
        "mean_gap_mean",
        "min_gap_mean",
        "max_gap_mean",
        "range_mean",
        "minimum_mean",
        "maximum_mean",
        "consecutive_rate",
    ]

    distributions = {
        name: []
        for name in metric_names
    }

    progress_interval = (
        MONTE_CARLO_EXPERIMENTS
        // 10
    )

    for experiment_no in range(
        1,
        MONTE_CARLO_EXPERIMENTS + 1,
    ):

        tickets = [
            make_random_ticket(
                rng
            )
            for _ in range(
                EXPECTED_ROWS
            )
        ]

        metrics = (
            calculate_sample_metrics(
                tickets
            )
        )

        for name in metric_names:
            distributions[
                name
            ].append(
                metrics[name]
            )

        if (
            progress_interval > 0
            and experiment_no
            % progress_interval == 0
        ):
            print(
                f"[PROGRESS] "
                f"{experiment_no:,} "
                f"/ "
                f"{MONTE_CARLO_EXPERIMENTS:,}"
            )

    return distributions


def empirical_two_sided_p_value(
    observed,
    simulated_values,
):
    null_mean = (
        statistics.mean(
            simulated_values
        )
    )

    observed_distance = abs(
        observed - null_mean
    )

    extreme = sum(
        1
        for value
        in simulated_values
        if abs(
            value - null_mean
        ) >= observed_distance
    )

    return (
        extreme + 1
    ) / (
        len(simulated_values)
        + 1
    )


def calculate_z_score(
    observed,
    simulated_values,
):
    null_mean = (
        statistics.mean(
            simulated_values
        )
    )

    null_sd = (
        statistics.stdev(
            simulated_values
        )
    )

    if null_sd == 0:
        return 0.0

    return (
        observed - null_mean
    ) / null_sd


def calculate_percentile_interval(
    simulated_values,
):
    ordered = sorted(
        simulated_values
    )

    n = len(ordered)

    lower_index = int(
        0.025 * n
    )

    upper_index = int(
        0.975 * n
    )

    upper_index = min(
        upper_index,
        n - 1,
    )

    return (
        ordered[
            lower_index
        ],
        ordered[
            upper_index
        ],
    )


def bonferroni_threshold(
    number_of_tests,
):
    return (
        ALPHA
        / number_of_tests
    )


def analyze(
    historical_metrics,
    null_distributions,
):
    rows = []

    metric_labels = {
        "sum_mean":
            "Sum mean",

        "mean_gap_mean":
            "Mean gap",

        "min_gap_mean":
            "Minimum gap",

        "max_gap_mean":
            "Maximum gap",

        "range_mean":
            "Range",

        "minimum_mean":
            "Minimum number",

        "maximum_mean":
            "Maximum number",

        "consecutive_rate":
            "Consecutive draw rate",
    }

    number_of_tests = len(
        metric_labels
    )

    corrected_alpha = (
        bonferroni_threshold(
            number_of_tests
        )
    )

    for metric_name, label in (
        metric_labels.items()
    ):

        observed = (
            historical_metrics[
                metric_name
            ]
        )

        simulated = (
            null_distributions[
                metric_name
            ]
        )

        null_mean = (
            statistics.mean(
                simulated
            )
        )

        null_sd = (
            statistics.stdev(
                simulated
            )
        )

        p_value = (
            empirical_two_sided_p_value(
                observed,
                simulated,
            )
        )

        z_score = (
            calculate_z_score(
                observed,
                simulated,
            )
        )

        ci_low, ci_high = (
            calculate_percentile_interval(
                simulated
            )
        )

        nominal_significant = (
            p_value < ALPHA
        )

        corrected_significant = (
            p_value
            < corrected_alpha
        )

        rows.append(
            {
                "metric":
                    metric_name,

                "label":
                    label,

                "observed":
                    observed,

                "null_mean":
                    null_mean,

                "difference":
                    observed
                    - null_mean,

                "null_sd":
                    null_sd,

                "z_score":
                    z_score,

                "p_value":
                    p_value,

                "null_95_low":
                    ci_low,

                "null_95_high":
                    ci_high,

                "nominal_significant":
                    nominal_significant,

                "bonferroni_alpha":
                    corrected_alpha,

                "bonferroni_significant":
                    corrected_significant,
            }
        )

    return rows


def save_csv(
    rows,
    output_file,
):
    fieldnames = [
        "metric",
        "label",
        "observed",
        "null_mean",
        "difference",
        "null_sd",
        "z_score",
        "p_value",
        "null_95_low",
        "null_95_high",
        "nominal_significant",
        "bonferroni_alpha",
        "bonferroni_significant",
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


def save_summary(
    rows,
    output_file,
):
    corrected_alpha = (
        rows[0][
            "bonferroni_alpha"
        ]
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Singapore TOTO 6/49\n"
        )

        file.write(
            "Combination Structure "
            "Significance Test\n"
        )

        file.write(
            "=" * 72
            + "\n\n"
        )

        file.write(
            f"Historical sample size : "
            f"{EXPECTED_ROWS}\n"
        )

        file.write(
            f"Monte Carlo experiments: "
            f"{MONTE_CARLO_EXPERIMENTS:,}\n"
        )

        file.write(
            f"Nominal alpha          : "
            f"{ALPHA}\n"
        )

        file.write(
            f"Bonferroni alpha       : "
            f"{corrected_alpha:.6f}\n\n"
        )

        for row in rows:

            file.write(
                f"{row['label']}\n"
            )

            file.write(
                "-" * 72
                + "\n"
            )

            file.write(
                "Observed       : "
                f"{row['observed']:.6f}\n"
            )

            file.write(
                "Random mean    : "
                f"{row['null_mean']:.6f}\n"
            )

            file.write(
                "Difference     : "
                f"{row['difference']:+.6f}\n"
            )

            file.write(
                "Z-score        : "
                f"{row['z_score']:+.4f}\n"
            )

            file.write(
                "Empirical p    : "
                f"{row['p_value']:.6f}\n"
            )

            file.write(
                "Random 95%     : "
                f"{row['null_95_low']:.6f}"
                " - "
                f"{row['null_95_high']:.6f}\n"
            )

            file.write(
                "p < 0.05       : "
                f"{row['nominal_significant']}\n"
            )

            file.write(
                "Bonferroni sig : "
                f"{row['bonferroni_significant']}\n\n"
            )

        nominal = [
            row
            for row in rows
            if row[
                "nominal_significant"
            ]
        ]

        corrected = [
            row
            for row in rows
            if row[
                "bonferroni_significant"
            ]
        ]

        file.write(
            "=" * 72
            + "\n"
        )

        file.write(
            "FINAL INTERPRETATION\n"
        )

        file.write(
            "=" * 72
            + "\n"
        )

        file.write(
            f"Nominal significant metrics : "
            f"{len(nominal)}\n"
        )

        file.write(
            f"After Bonferroni correction : "
            f"{len(corrected)}\n\n"
        )

        if not corrected:

            file.write(
                "No tested structural feature remains "
                "statistically significant after "
                "multiple-testing correction.\n"
            )

            file.write(
                "The observed historical structure is "
                "therefore compatible with variation "
                "expected from random 6/49 sampling.\n"
            )

        else:

            file.write(
                "At least one structural feature remains "
                "significant after multiple-testing "
                "correction.\n"
            )

            file.write(
                "Such features require independent-period "
                "replication before any predictive "
                "interpretation is justified.\n"
            )


def print_results(rows):
    print()
    print("=" * 90)

    print(
        "COMBINATION STRUCTURE "
        "SIGNIFICANCE TEST"
    )

    print("=" * 90)

    print(
        f"{'Metric':<24} "
        f"{'Observed':>10} "
        f"{'Random':>10} "
        f"{'Z':>8} "
        f"{'p-value':>10} "
        f"{'Bonf.':>8}"
    )

    print("-" * 90)

    for row in rows:

        print(
            f"{row['label']:<24} "
            f"{row['observed']:>10.5f} "
            f"{row['null_mean']:>10.5f} "
            f"{row['z_score']:>+8.3f} "
            f"{row['p_value']:>10.6f} "
            f"{str(row['bonferroni_significant']):>8}"
        )

    nominal_count = sum(
        1
        for row in rows
        if row[
            "nominal_significant"
        ]
    )

    corrected_count = sum(
        1
        for row in rows
        if row[
            "bonferroni_significant"
        ]
    )

    print()
    print(
        "Nominal p < 0.05 : "
        f"{nominal_count}"
    )

    print(
        "After Bonferroni : "
        f"{corrected_count}"
    )


def main():
    (
        csv_file,
        results_dir,
    ) = get_project_paths()

    print()
    print("=" * 72)

    print(
        "Singapore TOTO 6/49 "
        "Combination Structure Significance Test"
    )

    print("=" * 72)

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
        "[START] Calculating historical metrics..."
    )

    historical_metrics = (
        get_historical_metrics(
            records
        )
    )

    print(
        "[START] Running "
        f"{MONTE_CARLO_EXPERIMENTS:,} "
        "Monte Carlo experiments..."
    )

    null_distributions = (
        generate_null_distributions()
    )

    rows = analyze(
        historical_metrics,
        null_distributions,
    )

    csv_output = (
        results_dir
        / "combination_structure_significance.csv"
    )

    txt_output = (
        results_dir
        / "combination_structure_significance_summary.txt"
    )

    save_csv(
        rows,
        csv_output,
    )

    save_summary(
        rows,
        txt_output,
    )

    print_results(
        rows
    )

    print()
    print("=" * 72)

    print(
        "OUTPUT FILES"
    )

    print("=" * 72)

    print(
        f"[FILE] {csv_output}"
    )

    print(
        f"[FILE] {txt_output}"
    )

    print()
    print(
        "[DONE] Combination structure "
        "significance test complete."
    )

    print("=" * 72)


if __name__ == "__main__":
    main()

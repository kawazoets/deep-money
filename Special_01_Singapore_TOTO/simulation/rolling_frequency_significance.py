import csv
import math
import random
import statistics
from collections import Counter
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49
# Rolling Frequency Significance / Robustness Test
#
# Purpose:
#   Test whether the small apparent advantage observed for
#   rolling-frequency strategies is robust or compatible
#   with random variation.
#
# Tests:
#   1. Compare multiple rolling windows.
#   2. Compare average matches with theoretical expectation.
#   3. Split the backtest into early and late periods.
#   4. Bootstrap confidence intervals for mean matches.
#   5. Permutation-style comparison against random tickets.
#
# Important:
#   This script is designed to challenge the hypothesis,
#   not to optimize a lottery strategy.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

BALL_MIN = 1
BALL_MAX = 49
PICKS_PER_TICKET = 6

WINDOWS = [
    10,
    15,
    20,
    25,
    30,
    40,
    50,
    75,
    100,
    150,
    200,
]

MIN_TRAINING_DRAWS = max(WINDOWS)

BOOTSTRAP_RUNS = 10000
PERMUTATION_RUNS = 10000

RANDOM_SEED = 20260902


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
            records.append(
                {
                    "draw_no": int(
                        row["draw_no"]
                    ),
                    "draw_date": row[
                        "draw_date"
                    ],
                    "numbers": sorted(
                        [
                            int(row["n1"]),
                            int(row["n2"]),
                            int(row["n3"]),
                            int(row["n4"]),
                            int(row["n5"]),
                            int(row["n6"]),
                        ]
                    ),
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
            "Unexpected first draw: "
            f"{records[0]['draw_no']}"
        )

    if records[-1]["draw_no"] != LAST_DRAW:
        raise ValueError(
            "Unexpected last draw: "
            f"{records[-1]['draw_no']}"
        )

    return records


def make_frequency_ticket(
    training_records,
    window,
):
    recent = training_records[
        -window:
    ]

    counter = Counter()

    for record in recent:
        counter.update(
            record["numbers"]
        )

    ranked = sorted(
        range(
            BALL_MIN,
            BALL_MAX + 1,
        ),
        key=lambda ball: (
            -counter[ball],
            ball,
        ),
    )

    return sorted(
        ranked[:PICKS_PER_TICKET]
    )


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


def count_matches(
    ticket,
    actual,
):
    return len(
        set(ticket)
        & set(actual)
    )


def theoretical_mean_matches():
    return (
        PICKS_PER_TICKET
        * PICKS_PER_TICKET
        / BALL_MAX
    )


def build_backtest(records):
    rng = random.Random(
        RANDOM_SEED
    )

    window_matches = {
        window: []
        for window in WINDOWS
    }

    random_matches = []

    draw_numbers = []
    draw_dates = []

    for index in range(
        MIN_TRAINING_DRAWS,
        len(records),
    ):

        training_records = (
            records[:index]
        )

        target = records[index]

        actual = target[
            "numbers"
        ]

        draw_numbers.append(
            target["draw_no"]
        )

        draw_dates.append(
            target["draw_date"]
        )

        random_ticket = (
            make_random_ticket(rng)
        )

        random_matches.append(
            count_matches(
                random_ticket,
                actual,
            )
        )

        for window in WINDOWS:

            ticket = (
                make_frequency_ticket(
                    training_records,
                    window,
                )
            )

            matches = (
                count_matches(
                    ticket,
                    actual,
                )
            )

            window_matches[
                window
            ].append(
                matches
            )

    return {
        "draw_numbers": draw_numbers,
        "draw_dates": draw_dates,
        "random_matches": random_matches,
        "window_matches": window_matches,
    }


def bootstrap_mean_ci(
    values,
    rng,
    runs=BOOTSTRAP_RUNS,
):
    n = len(values)

    bootstrap_means = []

    for _ in range(runs):

        sample_sum = 0

        for _ in range(n):
            sample_sum += values[
                rng.randrange(n)
            ]

        bootstrap_means.append(
            sample_sum / n
        )

    bootstrap_means.sort()

    lower_index = int(
        0.025 * runs
    )

    upper_index = int(
        0.975 * runs
    )

    lower = bootstrap_means[
        lower_index
    ]

    upper = bootstrap_means[
        min(
            upper_index,
            runs - 1,
        )
    ]

    return lower, upper


def paired_difference_stats(
    strategy,
    baseline,
):
    differences = [
        strategy_value
        - baseline_value
        for strategy_value,
        baseline_value
        in zip(
            strategy,
            baseline,
        )
    ]

    mean_difference = (
        statistics.mean(
            differences
        )
    )

    if len(differences) > 1:
        sd_difference = (
            statistics.stdev(
                differences
            )
        )
    else:
        sd_difference = 0.0

    if sd_difference == 0:
        standard_error = 0.0
        z_score = 0.0
    else:
        standard_error = (
            sd_difference
            / math.sqrt(
                len(differences)
            )
        )

        z_score = (
            mean_difference
            / standard_error
        )

    return {
        "differences": differences,
        "mean_difference":
            mean_difference,
        "sd_difference":
            sd_difference,
        "standard_error":
            standard_error,
        "z_score":
            z_score,
    }


def permutation_p_value(
    differences,
    rng,
    runs=PERMUTATION_RUNS,
):
    observed = abs(
        statistics.mean(
            differences
        )
    )

    n = len(differences)

    extreme = 0

    for _ in range(runs):

        total = 0.0

        for value in differences:

            if rng.random() < 0.5:
                total += value
            else:
                total -= value

        simulated_mean = (
            total / n
        )

        if (
            abs(simulated_mean)
            >= observed
        ):
            extreme += 1

    return (
        extreme + 1
    ) / (
        runs + 1
    )


def split_period_stats(values):
    midpoint = (
        len(values) // 2
    )

    early = values[
        :midpoint
    ]

    late = values[
        midpoint:
    ]

    return {
        "early_mean":
            statistics.mean(
                early
            ),
        "late_mean":
            statistics.mean(
                late
            ),
        "early_n":
            len(early),
        "late_n":
            len(late),
    }


def analyze(backtest):
    bootstrap_rng = (
        random.Random(
            RANDOM_SEED + 100
        )
    )

    permutation_rng = (
        random.Random(
            RANDOM_SEED + 200
        )
    )

    random_matches = (
        backtest[
            "random_matches"
        ]
    )

    theoretical_mean = (
        theoretical_mean_matches()
    )

    analysis_rows = []

    for window in WINDOWS:

        values = (
            backtest[
                "window_matches"
            ][window]
        )

        mean_matches = (
            statistics.mean(
                values
            )
        )

        bootstrap_low, (
            bootstrap_high
        ) = bootstrap_mean_ci(
            values,
            bootstrap_rng,
        )

        paired = (
            paired_difference_stats(
                values,
                random_matches,
            )
        )

        p_value = (
            permutation_p_value(
                paired[
                    "differences"
                ],
                permutation_rng,
            )
        )

        split = (
            split_period_stats(
                values
            )
        )

        random_split = (
            split_period_stats(
                random_matches
            )
        )

        better = sum(
            1
            for strategy,
            baseline
            in zip(
                values,
                random_matches,
            )
            if strategy > baseline
        )

        worse = sum(
            1
            for strategy,
            baseline
            in zip(
                values,
                random_matches,
            )
            if strategy < baseline
        )

        ties = (
            len(values)
            - better
            - worse
        )

        analysis_rows.append(
            {
                "window": window,
                "n": len(values),

                "mean_matches":
                    mean_matches,

                "theoretical_mean":
                    theoretical_mean,

                "difference_vs_theory":
                    mean_matches
                    - theoretical_mean,

                "bootstrap_95_low":
                    bootstrap_low,

                "bootstrap_95_high":
                    bootstrap_high,

                "random_mean":
                    statistics.mean(
                        random_matches
                    ),

                "mean_difference_vs_random":
                    paired[
                        "mean_difference"
                    ],

                "paired_z_score":
                    paired[
                        "z_score"
                    ],

                "permutation_p_value":
                    p_value,

                "better_than_random":
                    better,

                "worse_than_random":
                    worse,

                "ties":
                    ties,

                "early_mean":
                    split[
                        "early_mean"
                    ],

                "late_mean":
                    split[
                        "late_mean"
                    ],

                "random_early_mean":
                    random_split[
                        "early_mean"
                    ],

                "random_late_mean":
                    random_split[
                        "late_mean"
                    ],
            }
        )

    return analysis_rows


def save_csv(
    rows,
    output_file,
):
    fieldnames = [
        "window",
        "n",
        "mean_matches",
        "theoretical_mean",
        "difference_vs_theory",
        "bootstrap_95_low",
        "bootstrap_95_high",
        "random_mean",
        "mean_difference_vs_random",
        "paired_z_score",
        "permutation_p_value",
        "better_than_random",
        "worse_than_random",
        "ties",
        "early_mean",
        "late_mean",
        "random_early_mean",
        "random_late_mean",
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

        writer.writerows(rows)


def save_summary(
    rows,
    output_file,
):
    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Singapore TOTO 6/49\n"
        )

        file.write(
            "Rolling Frequency "
            "Significance / Robustness Test\n"
        )

        file.write(
            "=" * 70
            + "\n\n"
        )

        file.write(
            "Theoretical expected matches "
            "for any fixed 6-number ticket:\n"
        )

        file.write(
            f"{theoretical_mean_matches():.6f}\n\n"
        )

        for row in rows:

            file.write(
                f"WINDOW {row['window']}\n"
            )

            file.write(
                "-" * 70
                + "\n"
            )

            file.write(
                "Mean matches              : "
                f"{row['mean_matches']:.6f}\n"
            )

            file.write(
                "95% bootstrap interval    : "
                f"{row['bootstrap_95_low']:.6f}"
                " - "
                f"{row['bootstrap_95_high']:.6f}\n"
            )

            file.write(
                "Random mean               : "
                f"{row['random_mean']:.6f}\n"
            )

            file.write(
                "Mean difference vs random : "
                f"{row['mean_difference_vs_random']:+.6f}\n"
            )

            file.write(
                "Permutation p-value        : "
                f"{row['permutation_p_value']:.6f}\n"
            )

            file.write(
                "Early-period mean          : "
                f"{row['early_mean']:.6f}\n"
            )

            file.write(
                "Late-period mean           : "
                f"{row['late_mean']:.6f}\n"
            )

            file.write(
                "Better / Worse / Tie       : "
                f"{row['better_than_random']} / "
                f"{row['worse_than_random']} / "
                f"{row['ties']}\n\n"
            )

        best = max(
            rows,
            key=lambda row:
            row["mean_matches"],
        )

        file.write(
            "=" * 70
            + "\n"
        )

        file.write(
            "BEST OBSERVED WINDOW\n"
        )

        file.write(
            "=" * 70
            + "\n"
        )

        file.write(
            f"Window: {best['window']}\n"
        )

        file.write(
            "Mean matches: "
            f"{best['mean_matches']:.6f}\n"
        )

        file.write(
            "Permutation p-value: "
            f"{best['permutation_p_value']:.6f}\n\n"
        )

        file.write(
            "CAUTION\n"
        )

        file.write(
            "The best-performing window was selected "
            "after comparing multiple windows.\n"
        )

        file.write(
            "Therefore its raw p-value must not be "
            "interpreted as proof of predictive power.\n"
        )

        file.write(
            "A genuine signal should remain visible "
            "across independent periods and future draws.\n"
        )


def print_results(rows):
    print()
    print("=" * 78)

    print(
        "ROLLING FREQUENCY "
        "SIGNIFICANCE / ROBUSTNESS TEST"
    )

    print("=" * 78)

    print(
        "Theory mean: "
        f"{theoretical_mean_matches():.6f}"
    )

    print()

    print(
        f"{'Window':>6} "
        f"{'Mean':>9} "
        f"{'DiffRnd':>10} "
        f"{'p-value':>10} "
        f"{'Early':>9} "
        f"{'Late':>9}"
    )

    print("-" * 78)

    for row in rows:

        print(
            f"{row['window']:>6} "
            f"{row['mean_matches']:>9.6f} "
            f"{row['mean_difference_vs_random']:>+10.6f} "
            f"{row['permutation_p_value']:>10.6f} "
            f"{row['early_mean']:>9.6f} "
            f"{row['late_mean']:>9.6f}"
        )

    best = max(
        rows,
        key=lambda row:
        row["mean_matches"],
    )

    print()
    print(
        "Best observed window: "
        f"{best['window']}"
    )

    print(
        "Best observed mean  : "
        f"{best['mean_matches']:.6f}"
    )

    print(
        "Raw permutation p   : "
        f"{best['permutation_p_value']:.6f}"
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
        "Rolling Frequency Robustness Test"
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
        "[START] Building walk-forward tests..."
    )

    backtest = (
        build_backtest(
            records
        )
    )

    print(
        "[START] Running bootstrap "
        "and permutation tests..."
    )

    rows = analyze(
        backtest
    )

    csv_output = (
        results_dir
        / "rolling_frequency_significance.csv"
    )

    txt_output = (
        results_dir
        / "rolling_frequency_significance_summary.txt"
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
    print("=" * 70)

    print(
        "OUTPUT FILES"
    )

    print("=" * 70)

    print(
        f"[FILE] {csv_output}"
    )

    print(
        f"[FILE] {txt_output}"
    )

    print()
    print(
        "[DONE] Robustness test complete."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()

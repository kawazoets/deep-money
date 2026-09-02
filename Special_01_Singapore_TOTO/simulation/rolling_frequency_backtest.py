import csv
import random
from collections import Counter
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49 Rolling Frequency Walk-Forward Backtest
#
# Purpose:
#   Test whether recent number frequency contains useful
#   information for the next real TOTO draw.
#
# Rolling windows:
#   20 draws
#   50 draws
#   100 draws
#
# Method:
#   - Use only past draws.
#   - For each target draw, calculate number frequencies
#     over the selected recent window.
#   - Pick the six most frequent numbers.
#   - Compare with the actual next draw.
#
# Baseline:
#   Pure random 6-number ticket.
#
# Important:
#   No future draw information is used.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

BALL_MIN = 1
BALL_MAX = 49
PICKS_PER_TICKET = 6

WINDOWS = [20, 50, 100]
MIN_TRAINING_DRAWS = max(WINDOWS)

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
            script_dir.parent
            / "toto_draws_6of49.csv"
        )

        if not csv_file.exists():
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
                    "draw_no": int(row["draw_no"]),
                    "draw_date": row["draw_date"],
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
        key=lambda record: record["draw_no"]
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


def build_frequency(records):
    counter = Counter()

    for record in records:
        counter.update(
            record["numbers"]
        )

    return counter


def make_rolling_ticket(
    training_records,
    window,
):
    recent_records = (
        training_records[-window:]
    )

    frequency = build_frequency(
        recent_records
    )

    ranked = sorted(
        (
            (
                ball,
                frequency[ball],
            )
            for ball in range(
                BALL_MIN,
                BALL_MAX + 1,
            )
        ),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    selected = [
        ball
        for ball, _ in ranked[
            :PICKS_PER_TICKET
        ]
    ]

    return sorted(selected)


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
    actual_numbers,
):
    return len(
        set(ticket)
        & set(actual_numbers)
    )


def run_backtest(records):
    rng = random.Random(
        RANDOM_SEED
    )

    results_by_window = {}

    for window in WINDOWS:
        results_by_window[window] = {
            "match_distribution": Counter(),
            "total_matches": 0,
            "better": 0,
            "worse": 0,
            "ties": 0,
        }

    random_distribution = Counter()
    random_total_matches = 0

    detail_rows = []

    for index in range(
        MIN_TRAINING_DRAWS,
        len(records),
    ):

        training_records = (
            records[:index]
        )

        target_record = (
            records[index]
        )

        actual_numbers = (
            target_record["numbers"]
        )

        random_ticket = (
            make_random_ticket(
                rng
            )
        )

        random_matches = (
            count_matches(
                random_ticket,
                actual_numbers,
            )
        )

        random_distribution[
            random_matches
        ] += 1

        random_total_matches += (
            random_matches
        )

        row = {
            "draw_no": target_record[
                "draw_no"
            ],
            "draw_date": target_record[
                "draw_date"
            ],
            "actual_numbers": "-".join(
                str(number)
                for number in actual_numbers
            ),
            "random_ticket": "-".join(
                str(number)
                for number in random_ticket
            ),
            "random_matches": random_matches,
        }

        for window in WINDOWS:

            rolling_ticket = (
                make_rolling_ticket(
                    training_records,
                    window,
                )
            )

            rolling_matches = (
                count_matches(
                    rolling_ticket,
                    actual_numbers,
                )
            )

            window_result = (
                results_by_window[
                    window
                ]
            )

            window_result[
                "match_distribution"
            ][rolling_matches] += 1

            window_result[
                "total_matches"
            ] += rolling_matches

            if (
                rolling_matches
                > random_matches
            ):
                window_result[
                    "better"
                ] += 1

            elif (
                rolling_matches
                < random_matches
            ):
                window_result[
                    "worse"
                ] += 1

            else:
                window_result[
                    "ties"
                ] += 1

            row[
                f"window_{window}_ticket"
            ] = "-".join(
                str(number)
                for number in rolling_ticket
            )

            row[
                f"window_{window}_matches"
            ] = rolling_matches

        detail_rows.append(row)

    return {
        "detail_rows": detail_rows,
        "random_distribution":
            random_distribution,
        "random_total_matches":
            random_total_matches,
        "results_by_window":
            results_by_window,
    }


def save_detail_csv(
    results,
    output_file,
):
    fieldnames = [
        "draw_no",
        "draw_date",
        "actual_numbers",
        "random_ticket",
        "random_matches",
    ]

    for window in WINDOWS:
        fieldnames.extend(
            [
                f"window_{window}_ticket",
                f"window_{window}_matches",
            ]
        )

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
            results["detail_rows"]
        )


def save_summary(
    results,
    output_file,
):
    test_count = len(
        results["detail_rows"]
    )

    random_average = (
        results[
            "random_total_matches"
        ]
        / test_count
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Singapore TOTO 6/49 "
            "Rolling Frequency Walk-Forward Backtest\n"
        )

        file.write(
            "=" * 60
            + "\n\n"
        )

        file.write(
            f"Backtest draws : "
            f"{test_count}\n"
        )

        file.write(
            f"Random average : "
            f"{random_average:.6f}\n\n"
        )

        for window in WINDOWS:

            window_result = (
                results[
                    "results_by_window"
                ][window]
            )

            average = (
                window_result[
                    "total_matches"
                ]
                / test_count
            )

            file.write(
                f"WINDOW {window}\n"
            )

            file.write(
                "-" * 60
                + "\n"
            )

            file.write(
                f"Average matches : "
                f"{average:.6f}\n"
            )

            file.write(
                f"Better than random : "
                f"{window_result['better']}\n"
            )

            file.write(
                f"Worse than random  : "
                f"{window_result['worse']}\n"
            )

            file.write(
                f"Ties               : "
                f"{window_result['ties']}\n\n"
            )

            file.write(
                "Match distribution\n"
            )

            for matches in range(
                0,
                PICKS_PER_TICKET + 1,
            ):

                count = (
                    window_result[
                        "match_distribution"
                    ][matches]
                )

                file.write(
                    f"  {matches}: "
                    f"{count}\n"
                )

            file.write("\n")

        file.write(
            "INTERPRETATION NOTE\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            "Each prediction uses only recent draws "
            "that occurred before the target draw.\n"
        )

        file.write(
            "A rolling-frequency strategy would need "
            "to outperform the random baseline "
            "consistently across many future draws "
            "to indicate useful predictive information.\n"
        )


def print_summary(
    results,
):
    test_count = len(
        results["detail_rows"]
    )

    random_average = (
        results[
            "random_total_matches"
        ]
        / test_count
    )

    print()
    print("=" * 60)
    print(
        "ROLLING FREQUENCY WALK-FORWARD BACKTEST"
    )
    print("=" * 60)

    print(
        f"Backtest draws : "
        f"{test_count}"
    )

    print(
        f"Random average : "
        f"{random_average:.6f}"
    )

    for window in WINDOWS:

        window_result = (
            results[
                "results_by_window"
            ][window]
        )

        average = (
            window_result[
                "total_matches"
            ]
            / test_count
        )

        print()
        print(
            f"Window {window}"
        )

        print(
            f"Average matches : "
            f"{average:.6f}"
        )

        print(
            f"Better than random : "
            f"{window_result['better']}"
        )

        print(
            f"Worse than random  : "
            f"{window_result['worse']}"
        )

        print(
            f"Ties               : "
            f"{window_result['ties']}"
        )


def main():
    (
        csv_file,
        results_dir,
    ) = get_project_paths()

    print()
    print("=" * 60)
    print(
        "Singapore TOTO 6/49 "
        "Rolling Frequency Backtest"
    )
    print("=" * 60)

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
        "[START] Running walk-forward backtest..."
    )

    results = run_backtest(
        records
    )

    detail_file = (
        results_dir
        / "rolling_frequency_backtest_results.csv"
    )

    summary_file = (
        results_dir
        / "rolling_frequency_backtest_summary.txt"
    )

    save_detail_csv(
        results,
        detail_file,
    )

    save_summary(
        results,
        summary_file,
    )

    print_summary(
        results
    )

    print()
    print("=" * 60)
    print(
        "OUTPUT FILES"
    )
    print("=" * 60)

    print(
        f"[FILE] {detail_file}"
    )

    print(
        f"[FILE] {summary_file}"
    )

    print()
    print(
        "[DONE] Rolling frequency backtest complete."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

import csv
import math
import statistics
from collections import Counter
from itertools import combinations
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49 Historical Frequency Analysis
#
# Dataset:
#   Draw 2995 - 4213
#   09 Oct 2014 - 31 Aug 2026
#   1,219 draws
#
# Purpose:
#   Describe historical patterns.
#
# Important:
#   Historical frequency does NOT imply that a number has
#   a higher probability of appearing in a future fair draw.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

BALL_MIN = 1
BALL_MAX = 49
MAIN_BALLS_PER_DRAW = 6


def get_project_paths():
    """
    Locate the dataset and output directory.

    Repository structure:

        Special_01_Singapore_TOTO/
        ├── data/
        │   └── toto_draws_6of49.csv
        ├── results/
        └── scripts/
            └── analyze_frequency.py

    If downloaded directly into Downloads,
    the script looks for the CSV beside itself and creates
    a results folder beside itself.
    """

    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    if script_dir.name.lower() == "scripts":
        project_dir = script_dir.parent
        csv_file = (
            project_dir
            / "data"
            / "toto_draws_6of49.csv"
        )
        results_dir = project_dir / "results"

    else:
        csv_file = (
            script_dir
            / "toto_draws_6of49.csv"
        )
        results_dir = script_dir / "results"

    if not csv_file.exists():
        raise FileNotFoundError(
            f"Dataset not found: {csv_file}"
        )

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        csv_file,
        results_dir,
    )


def load_dataset(csv_file):
    records = []

    with csv_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            numbers = [
                int(row["n1"]),
                int(row["n2"]),
                int(row["n3"]),
                int(row["n4"]),
                int(row["n5"]),
                int(row["n6"]),
            ]

            records.append(
                {
                    "draw_no": int(row["draw_no"]),
                    "draw_date": row["draw_date"],
                    "numbers": numbers,
                    "additional": int(
                        row["additional"]
                    ),
                }
            )

    return records


def validate_dataset(records):
    if len(records) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} draws, "
            f"found {len(records)}."
        )

    draw_numbers = [
        record["draw_no"]
        for record in records
    ]

    if min(draw_numbers) != FIRST_DRAW:
        raise ValueError(
            f"Unexpected first draw: "
            f"{min(draw_numbers)}"
        )

    if max(draw_numbers) != LAST_DRAW:
        raise ValueError(
            f"Unexpected last draw: "
            f"{max(draw_numbers)}"
        )


def calculate_main_frequency(records):
    counter = Counter()

    for record in records:
        counter.update(
            record["numbers"]
        )

    return counter


def calculate_additional_frequency(records):
    counter = Counter()

    for record in records:
        counter.update(
            [record["additional"]]
        )

    return counter


def calculate_expected_main_count(
    number_of_draws,
):
    return (
        number_of_draws
        * MAIN_BALLS_PER_DRAW
        / 49
    )


def calculate_standard_deviation_main(
    number_of_draws,
):
    """
    Approximate standard deviation for the number of draws
    in which a particular number appears.

    For one number:

        p = 6 / 49

    Each draw contributes either:
        appears = 1
        absent  = 0
    """

    p = MAIN_BALLS_PER_DRAW / 49

    return math.sqrt(
        number_of_draws
        * p
        * (1 - p)
    )


def save_frequency_table(
    main_frequency,
    additional_frequency,
    number_of_draws,
    output_file,
):
    expected_main = (
        calculate_expected_main_count(
            number_of_draws
        )
    )

    main_sd = (
        calculate_standard_deviation_main(
            number_of_draws
        )
    )

    expected_additional = (
        number_of_draws / 49
    )

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "ball",
                "main_frequency",
                "main_expected",
                "main_difference",
                "main_z_score",
                "additional_frequency",
                "additional_expected",
            ]
        )

        for ball in range(
            BALL_MIN,
            BALL_MAX + 1,
        ):

            observed = (
                main_frequency[ball]
            )

            difference = (
                observed - expected_main
            )

            z_score = (
                difference / main_sd
            )

            writer.writerow(
                [
                    ball,
                    observed,
                    round(expected_main, 3),
                    round(difference, 3),
                    round(z_score, 3),
                    additional_frequency[ball],
                    round(
                        expected_additional,
                        3,
                    ),
                ]
            )


def calculate_odd_even(records):
    distribution = Counter()

    for record in records:

        odd_count = sum(
            1
            for number in record["numbers"]
            if number % 2 == 1
        )

        even_count = (
            MAIN_BALLS_PER_DRAW
            - odd_count
        )

        distribution[
            (odd_count, even_count)
        ] += 1

    return distribution


def calculate_low_high(records):
    """
    Low:
        1 - 24

    High:
        25 - 49
    """

    distribution = Counter()

    for record in records:

        low_count = sum(
            1
            for number in record["numbers"]
            if number <= 24
        )

        high_count = (
            MAIN_BALLS_PER_DRAW
            - low_count
        )

        distribution[
            (low_count, high_count)
        ] += 1

    return distribution


def calculate_sum_statistics(records):
    sums = [
        sum(record["numbers"])
        for record in records
    ]

    return {
        "mean": statistics.mean(sums),
        "median": statistics.median(sums),
        "stdev": statistics.stdev(sums),
        "minimum": min(sums),
        "maximum": max(sums),
    }


def contains_consecutive_numbers(
    numbers,
):
    ordered = sorted(numbers)

    for left, right in zip(
        ordered,
        ordered[1:],
    ):
        if right - left == 1:
            return True

    return False


def calculate_consecutive_statistics(
    records,
):
    with_consecutive = sum(
        1
        for record in records
        if contains_consecutive_numbers(
            record["numbers"]
        )
    )

    without_consecutive = (
        len(records)
        - with_consecutive
    )

    percentage = (
        with_consecutive
        / len(records)
        * 100
    )

    return {
        "with": with_consecutive,
        "without": without_consecutive,
        "percentage": percentage,
    }


def calculate_pair_frequency(records):
    pair_counter = Counter()

    for record in records:

        for pair in combinations(
            sorted(record["numbers"]),
            2,
        ):
            pair_counter[pair] += 1

    return pair_counter


def save_pair_frequency(
    pair_counter,
    output_file,
):
    ranked = pair_counter.most_common()

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "number_1",
                "number_2",
                "frequency",
            ]
        )

        for (
            number_1,
            number_2,
        ), frequency in ranked:

            writer.writerow(
                [
                    number_1,
                    number_2,
                    frequency,
                ]
            )


def calculate_chi_square(
    main_frequency,
    number_of_draws,
):
    """
    Descriptive chi-square statistic only.

    This script intentionally does not claim that a large or
    small statistic demonstrates predictability.
    """

    expected = (
        calculate_expected_main_count(
            number_of_draws
        )
    )

    statistic = 0.0

    for ball in range(
        BALL_MIN,
        BALL_MAX + 1,
    ):

        observed = (
            main_frequency[ball]
        )

        statistic += (
            (observed - expected) ** 2
            / expected
        )

    return statistic


def write_summary(
    records,
    main_frequency,
    additional_frequency,
    odd_even,
    low_high,
    sum_stats,
    consecutive_stats,
    pair_counter,
    chi_square,
    output_file,
):
    number_of_draws = len(records)

    expected_main = (
        calculate_expected_main_count(
            number_of_draws
        )
    )

    ranked_main = sorted(
        main_frequency.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    ranked_additional = sorted(
        additional_frequency.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Singapore TOTO 6/49 "
            "Historical Frequency Analysis\n"
        )

        file.write(
            "=" * 60 + "\n\n"
        )

        file.write(
            f"Draw range: "
            f"{FIRST_DRAW} - {LAST_DRAW}\n"
        )

        file.write(
            f"Number of draws: "
            f"{number_of_draws}\n"
        )

        file.write(
            f"Expected main frequency "
            f"per number: "
            f"{expected_main:.3f}\n\n"
        )

        file.write(
            "MOST FREQUENT MAIN NUMBERS\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        for ball, frequency in ranked_main[:10]:
            file.write(
                f"{ball:>2}: {frequency}\n"
            )

        file.write("\n")

        file.write(
            "LEAST FREQUENT MAIN NUMBERS\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        for ball, frequency in sorted(
            main_frequency.items(),
            key=lambda item: (
                item[1],
                item[0],
            ),
        )[:10]:

            file.write(
                f"{ball:>2}: {frequency}\n"
            )

        file.write("\n")

        file.write(
            "MOST FREQUENT ADDITIONAL NUMBERS\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        for (
            ball,
            frequency,
        ) in ranked_additional[:10]:

            file.write(
                f"{ball:>2}: {frequency}\n"
            )

        file.write("\n")

        file.write(
            "ODD / EVEN DISTRIBUTION\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        for odd_count in range(7):

            even_count = (
                MAIN_BALLS_PER_DRAW
                - odd_count
            )

            count = odd_even[
                (
                    odd_count,
                    even_count,
                )
            ]

            percentage = (
                count
                / number_of_draws
                * 100
            )

            file.write(
                f"{odd_count} odd / "
                f"{even_count} even: "
                f"{count} "
                f"({percentage:.2f}%)\n"
            )

        file.write("\n")

        file.write(
            "LOW / HIGH DISTRIBUTION\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        for low_count in range(7):

            high_count = (
                MAIN_BALLS_PER_DRAW
                - low_count
            )

            count = low_high[
                (
                    low_count,
                    high_count,
                )
            ]

            percentage = (
                count
                / number_of_draws
                * 100
            )

            file.write(
                f"{low_count} low / "
                f"{high_count} high: "
                f"{count} "
                f"({percentage:.2f}%)\n"
            )

        file.write("\n")

        file.write(
            "SUM OF SIX MAIN NUMBERS\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        file.write(
            f"Mean   : "
            f"{sum_stats['mean']:.3f}\n"
        )

        file.write(
            f"Median : "
            f"{sum_stats['median']:.3f}\n"
        )

        file.write(
            f"Stdev  : "
            f"{sum_stats['stdev']:.3f}\n"
        )

        file.write(
            f"Minimum: "
            f"{sum_stats['minimum']}\n"
        )

        file.write(
            f"Maximum: "
            f"{sum_stats['maximum']}\n"
        )

        file.write("\n")

        file.write(
            "CONSECUTIVE NUMBERS\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        file.write(
            f"Draws containing at least "
            f"one consecutive pair: "
            f"{consecutive_stats['with']}\n"
        )

        file.write(
            f"Percentage: "
            f"{consecutive_stats['percentage']:.2f}%\n"
        )

        file.write("\n")

        file.write(
            "MOST FREQUENT MAIN-NUMBER PAIRS\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        for (
            pair,
            frequency,
        ) in pair_counter.most_common(20):

            file.write(
                f"{pair[0]:>2} + "
                f"{pair[1]:>2}: "
                f"{frequency}\n"
            )

        file.write("\n")

        file.write(
            "CHI-SQUARE DESCRIPTIVE STATISTIC\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        file.write(
            f"{chi_square:.6f}\n\n"
        )

        file.write(
            "Interpretation note:\n"
        )

        file.write(
            "Historical deviations from equal frequency "
            "do not by themselves provide evidence that "
            "future fair lottery draws are predictable.\n"
        )


def print_top_bottom(
    main_frequency,
    number_of_draws,
):
    expected = (
        calculate_expected_main_count(
            number_of_draws
        )
    )

    ranked = sorted(
        main_frequency.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    print()
    print("=" * 60)
    print("MAIN NUMBER FREQUENCY")
    print("=" * 60)

    print(
        f"Expected frequency per number: "
        f"{expected:.3f}"
    )

    print()
    print("Top 10:")

    for ball, count in ranked[:10]:
        print(
            f"  {ball:>2} -> {count}"
        )

    print()
    print("Bottom 10:")

    for ball, count in sorted(
        main_frequency.items(),
        key=lambda item: (
            item[1],
            item[0],
        ),
    )[:10]:

        print(
            f"  {ball:>2} -> {count}"
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
        "Historical Frequency Analysis"
    )
    print("=" * 60)

    print(
        f"Dataset: {csv_file}"
    )

    records = load_dataset(
        csv_file
    )

    validate_dataset(
        records
    )

    print(
        f"Draws loaded: {len(records)}"
    )

    main_frequency = (
        calculate_main_frequency(
            records
        )
    )

    additional_frequency = (
        calculate_additional_frequency(
            records
        )
    )

    odd_even = (
        calculate_odd_even(
            records
        )
    )

    low_high = (
        calculate_low_high(
            records
        )
    )

    sum_stats = (
        calculate_sum_statistics(
            records
        )
    )

    consecutive_stats = (
        calculate_consecutive_statistics(
            records
        )
    )

    pair_counter = (
        calculate_pair_frequency(
            records
        )
    )

    chi_square = (
        calculate_chi_square(
            main_frequency,
            len(records),
        )
    )

    frequency_file = (
        results_dir
        / "frequency_analysis.csv"
    )

    pair_file = (
        results_dir
        / "pair_frequency.csv"
    )

    summary_file = (
        results_dir
        / "frequency_summary.txt"
    )

    save_frequency_table(
        main_frequency,
        additional_frequency,
        len(records),
        frequency_file,
    )

    save_pair_frequency(
        pair_counter,
        pair_file,
    )

    write_summary(
        records,
        main_frequency,
        additional_frequency,
        odd_even,
        low_high,
        sum_stats,
        consecutive_stats,
        pair_counter,
        chi_square,
        summary_file,
    )

    print_top_bottom(
        main_frequency,
        len(records),
    )

    print()
    print("=" * 60)
    print("OUTPUT FILES")
    print("=" * 60)

    print(
        f"[FILE] {frequency_file}"
    )

    print(
        f"[FILE] {pair_file}"
    )

    print(
        f"[FILE] {summary_file}"
    )

    print()
    print(
        "[DONE] Historical analysis complete."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

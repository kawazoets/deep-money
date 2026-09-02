import csv
import random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49 Pair Strategy Walk-Forward Backtest
#
# Purpose:
#   Test whether historically frequent number-pairs contain
#   useful information for the next real TOTO draw.
#
# Method:
#   - Use only past draws.
#   - Build pair frequencies from the available history.
#   - Score candidate numbers from pair relationships.
#   - Predict six numbers for the next actual draw.
#   - Compare with the actual winning numbers.
#
# Baseline:
#   Pure random 6-number ticket.
#
# Important:
#   No future draw information is used to generate a prediction.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

BALL_MIN = 1
BALL_MAX = 49
PICKS_PER_TICKET = 6

MIN_TRAINING_DRAWS = 200

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


def build_pair_frequency(training_records):
    pair_counter = Counter()

    for record in training_records:
        for pair in combinations(
            record["numbers"],
            2,
        ):
            pair_counter[pair] += 1

    return pair_counter


def build_single_frequency(training_records):
    single_counter = Counter()

    for record in training_records:
        single_counter.update(
            record["numbers"]
        )

    return single_counter


def calculate_pair_scores(
    pair_counter,
    single_counter,
):
    """
    Give each ball a score based on:
      - how often it appears in historically common pairs
      - plus a small stabilizing contribution from
        single-number frequency
    """

    pair_score = defaultdict(float)

    for (
        number_a,
        number_b,
    ), frequency in pair_counter.items():

        pair_score[number_a] += frequency
        pair_score[number_b] += frequency

    scores = {}

    max_single = max(
        single_counter.values()
    )

    for ball in range(
        BALL_MIN,
        BALL_MAX + 1,
    ):

        single_component = (
            single_counter[ball]
            / max_single
            if max_single > 0
            else 0.0
        )

        scores[ball] = (
            pair_score[ball]
            + single_component
        )

    return scores


def make_pair_strategy_ticket(
    training_records,
):
    pair_counter = (
        build_pair_frequency(
            training_records
        )
    )

    single_counter = (
        build_single_frequency(
            training_records
        )
    )

    scores = calculate_pair_scores(
        pair_counter,
        single_counter,
    )

    ranked = sorted(
        scores.items(),
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

    pair_match_distribution = Counter()
    random_match_distribution = Counter()

    pair_total_matches = 0
    random_total_matches = 0

    pair_better = 0
    random_better = 0
    ties = 0

    rows = []

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

        pair_ticket = (
            make_pair_strategy_ticket(
                training_records
            )
        )

        random_ticket = (
            make_random_ticket(
                rng
            )
        )

        actual_numbers = (
            target_record["numbers"]
        )

        pair_matches = count_matches(
            pair_ticket,
            actual_numbers,
        )

        random_matches = count_matches(
            random_ticket,
            actual_numbers,
        )

        pair_match_distribution[
            pair_matches
        ] += 1

        random_match_distribution[
            random_matches
        ] += 1

        pair_total_matches += (
            pair_matches
        )

        random_total_matches += (
            random_matches
        )

        if pair_matches > random_matches:
            pair_better += 1

        elif random_matches > pair_matches:
            random_better += 1

        else:
            ties += 1

        rows.append(
            {
                "draw_no": target_record[
                    "draw_no"
                ],
                "draw_date": target_record[
                    "draw_date"
                ],
                "pair_ticket": "-".join(
                    str(number)
                    for number in pair_ticket
                ),
                "random_ticket": "-".join(
                    str(number)
                    for number in random_ticket
                ),
                "actual_numbers": "-".join(
                    str(number)
                    for number in actual_numbers
                ),
                "pair_matches": pair_matches,
                "random_matches": random_matches,
            }
        )

    return {
        "rows": rows,
        "pair_match_distribution":
            pair_match_distribution,
        "random_match_distribution":
            random_match_distribution,
        "pair_total_matches":
            pair_total_matches,
        "random_total_matches":
            random_total_matches,
        "pair_better": pair_better,
        "random_better": random_better,
        "ties": ties,
    }


def save_detail_csv(
    results,
    output_file,
):
    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "draw_no",
                "draw_date",
                "pair_ticket",
                "random_ticket",
                "actual_numbers",
                "pair_matches",
                "random_matches",
            ],
        )

        writer.writeheader()

        writer.writerows(
            results["rows"]
        )


def save_summary(
    results,
    output_file,
):
    test_count = len(
        results["rows"]
    )

    pair_average = (
        results[
            "pair_total_matches"
        ]
        / test_count
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
            "Pair Strategy Walk-Forward Backtest\n"
        )

        file.write(
            "=" * 60
            + "\n\n"
        )

        file.write(
            f"Total historical draws : "
            f"{EXPECTED_ROWS}\n"
        )

        file.write(
            f"Initial training draws : "
            f"{MIN_TRAINING_DRAWS}\n"
        )

        file.write(
            f"Backtest draws         : "
            f"{test_count}\n\n"
        )

        file.write(
            "AVERAGE MATCHES\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            f"Pair strategy   : "
            f"{pair_average:.6f}\n"
        )

        file.write(
            f"Random baseline : "
            f"{random_average:.6f}\n\n"
        )

        file.write(
            "HEAD-TO-HEAD\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            f"Pair better   : "
            f"{results['pair_better']}\n"
        )

        file.write(
            f"Random better : "
            f"{results['random_better']}\n"
        )

        file.write(
            f"Ties          : "
            f"{results['ties']}\n\n"
        )

        file.write(
            "MATCH DISTRIBUTION\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        for matches in range(
            0,
            PICKS_PER_TICKET + 1,
        ):

            pair_count = (
                results[
                    "pair_match_distribution"
                ][matches]
            )

            random_count = (
                results[
                    "random_match_distribution"
                ][matches]
            )

            file.write(
                f"{matches} matches\n"
            )

            file.write(
                f"  Pair   : "
                f"{pair_count}\n"
            )

            file.write(
                f"  Random : "
                f"{random_count}\n\n"
            )

        file.write(
            "INTERPRETATION NOTE\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            "This is an out-of-sample walk-forward test.\n"
        )

        file.write(
            "Each prediction uses only draws that occurred "
            "before the target draw.\n"
        )

        file.write(
            "A persistent advantage would require the pair "
            "strategy to outperform the random baseline across "
            "many future draws, not merely a small finite-sample "
            "difference.\n"
        )


def print_summary(
    results,
):
    test_count = len(
        results["rows"]
    )

    pair_average = (
        results[
            "pair_total_matches"
        ]
        / test_count
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
        "PAIR STRATEGY WALK-FORWARD BACKTEST"
    )
    print("=" * 60)

    print(
        f"Initial training draws : "
        f"{MIN_TRAINING_DRAWS}"
    )

    print(
        f"Backtest draws         : "
        f"{test_count}"
    )

    print()

    print(
        f"Average matches - Pair   : "
        f"{pair_average:.6f}"
    )

    print(
        f"Average matches - Random : "
        f"{random_average:.6f}"
    )

    print()

    print(
        f"Pair better   : "
        f"{results['pair_better']}"
    )

    print(
        f"Random better : "
        f"{results['random_better']}"
    )

    print(
        f"Ties          : "
        f"{results['ties']}"
    )

    print()

    print(
        f"{'Matches':>7} "
        f"{'Pair':>10} "
        f"{'Random':>10}"
    )

    for matches in range(
        0,
        PICKS_PER_TICKET + 1,
    ):

        pair_count = (
            results[
                "pair_match_distribution"
            ][matches]
        )

        random_count = (
            results[
                "random_match_distribution"
            ][matches]
        )

        print(
            f"{matches:>7} "
            f"{pair_count:>10} "
            f"{random_count:>10}"
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
        "Pair Strategy Backtest"
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
        / "pair_backtest_results.csv"
    )

    summary_file = (
        results_dir
        / "pair_backtest_summary.txt"
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
        "[DONE] Pair strategy backtest complete."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

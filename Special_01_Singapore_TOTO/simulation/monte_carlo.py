import csv
import random
from collections import Counter
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49 Monte Carlo Experiment
#
# Compare:
#   1. Pure random strategy
#   2. Historical-frequency weighted strategy
#
# Simulation runs:
#   1,000,000
#
# Important:
#   The simulated winning numbers are always generated
#   uniformly at random from 1 to 49.
#
#   Therefore this experiment does NOT assume that past
#   frequencies affect the next fair draw.
# ============================================================


FIRST_DRAW = 2995
LAST_DRAW = 4213
EXPECTED_ROWS = 1219

BALL_MIN = 1
BALL_MAX = 49
PICKS_PER_TICKET = 6

SIMULATIONS = 1_000_000
RANDOM_SEED = 20260901


def get_project_paths():
    """
    Repository structure:

        Special_01_Singapore_TOTO/
        ├── data/
        │   └── toto_draws_6of49.csv
        ├── results/
        └── simulation/
            └── monte_carlo.py

    If this file is downloaded directly into Downloads,
    it looks for the dataset in the Downloads directory.
    """

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
                [
                    int(row["n1"]),
                    int(row["n2"]),
                    int(row["n3"]),
                    int(row["n4"]),
                    int(row["n5"]),
                    int(row["n6"]),
                ]
            )

    if len(records) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} draws, "
            f"found {len(records)}"
        )

    return records


def calculate_historical_frequency(records):
    counter = Counter()

    for numbers in records:
        counter.update(numbers)

    return counter


def make_weight_list(frequency):
    """
    Create one weight per ball.

    Ball 1 corresponds to weights[0],
    Ball 49 corresponds to weights[48].
    """

    return [
        frequency[ball]
        for ball in range(
            BALL_MIN,
            BALL_MAX + 1,
        )
    ]


def weighted_ticket_without_replacement(
    rng,
    weights,
):
    """
    Select six unique numbers using historical frequency
    as sampling weight.

    Numbers are sampled one at a time without replacement.
    """

    available_numbers = list(
        range(
            BALL_MIN,
            BALL_MAX + 1,
        )
    )

    available_weights = list(weights)

    chosen = []

    for _ in range(PICKS_PER_TICKET):

        selected = rng.choices(
            available_numbers,
            weights=available_weights,
            k=1,
        )[0]

        index = available_numbers.index(
            selected
        )

        chosen.append(selected)

        del available_numbers[index]
        del available_weights[index]

    return sorted(chosen)


def random_ticket(rng):
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
    winning_numbers,
):
    return len(
        set(ticket)
        & set(winning_numbers)
    )


def run_simulation(
    frequency,
):
    weights = make_weight_list(
        frequency
    )

    rng = random.Random(
        RANDOM_SEED
    )

    random_results = Counter()
    weighted_results = Counter()

    random_total_matches = 0
    weighted_total_matches = 0

    random_wins = 0
    weighted_wins = 0
    ties = 0

    progress_interval = (
        SIMULATIONS // 10
    )

    for simulation_no in range(
        1,
        SIMULATIONS + 1,
    ):

        # --------------------------------------------
        # Simulated winning draw:
        # always fair / uniform
        # --------------------------------------------

        winning_numbers = random_ticket(
            rng
        )

        # --------------------------------------------
        # Strategy A:
        # pure random
        # --------------------------------------------

        random_pick = random_ticket(
            rng
        )

        # --------------------------------------------
        # Strategy B:
        # historical-frequency weighted
        # --------------------------------------------

        weighted_pick = (
            weighted_ticket_without_replacement(
                rng,
                weights,
            )
        )

        random_matches = count_matches(
            random_pick,
            winning_numbers,
        )

        weighted_matches = count_matches(
            weighted_pick,
            winning_numbers,
        )

        random_results[
            random_matches
        ] += 1

        weighted_results[
            weighted_matches
        ] += 1

        random_total_matches += (
            random_matches
        )

        weighted_total_matches += (
            weighted_matches
        )

        if random_matches > weighted_matches:
            random_wins += 1

        elif weighted_matches > random_matches:
            weighted_wins += 1

        else:
            ties += 1

        if (
            progress_interval > 0
            and simulation_no
            % progress_interval == 0
        ):
            print(
                f"[PROGRESS] "
                f"{simulation_no:,} "
                f"/ {SIMULATIONS:,}"
            )

    return {
        "random_results": random_results,
        "weighted_results": weighted_results,
        "random_total_matches": random_total_matches,
        "weighted_total_matches": weighted_total_matches,
        "random_wins": random_wins,
        "weighted_wins": weighted_wins,
        "ties": ties,
    }


def calculate_theoretical_match_probabilities():
    """
    Exact probability that two independently generated
    6-number tickets from 49 numbers share exactly k numbers.

    This is the reference distribution for a fair lottery.
    """

    from math import comb

    denominator = comb(
        BALL_MAX,
        PICKS_PER_TICKET,
    )

    probabilities = {}

    for k in range(
        0,
        PICKS_PER_TICKET + 1,
    ):

        if (
            PICKS_PER_TICKET - k
            > BALL_MAX - PICKS_PER_TICKET
        ):
            probability = 0.0

        else:
            probability = (
                comb(
                    PICKS_PER_TICKET,
                    k,
                )
                * comb(
                    BALL_MAX
                    - PICKS_PER_TICKET,
                    PICKS_PER_TICKET - k,
                )
                / denominator
            )

        probabilities[k] = probability

    return probabilities


def save_results(
    results,
    theoretical,
    output_file,
):
    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "matches",
                "random_count",
                "random_rate",
                "weighted_count",
                "weighted_rate",
                "theoretical_rate",
            ]
        )

        for matches in range(
            0,
            PICKS_PER_TICKET + 1,
        ):

            random_count = (
                results[
                    "random_results"
                ][matches]
            )

            weighted_count = (
                results[
                    "weighted_results"
                ][matches]
            )

            writer.writerow(
                [
                    matches,
                    random_count,
                    random_count
                    / SIMULATIONS,
                    weighted_count,
                    weighted_count
                    / SIMULATIONS,
                    theoretical[matches],
                ]
            )


def save_summary(
    results,
    theoretical,
    output_file,
):
    random_average = (
        results[
            "random_total_matches"
        ]
        / SIMULATIONS
    )

    weighted_average = (
        results[
            "weighted_total_matches"
        ]
        / SIMULATIONS
    )

    expected_average = (
        PICKS_PER_TICKET
        * PICKS_PER_TICKET
        / BALL_MAX
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Singapore TOTO 6/49 "
            "Monte Carlo Experiment\n"
        )

        file.write(
            "=" * 60
            + "\n\n"
        )

        file.write(
            f"Simulations : "
            f"{SIMULATIONS:,}\n"
        )

        file.write(
            f"Random seed : "
            f"{RANDOM_SEED}\n\n"
        )

        file.write(
            "STRATEGIES\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            "A: Pure random ticket\n"
        )

        file.write(
            "B: Historical-frequency "
            "weighted ticket\n\n"
        )

        file.write(
            "Winning draw generation:\n"
        )

        file.write(
            "Uniform random 6-from-49\n\n"
        )

        file.write(
            "AVERAGE MATCHES PER TICKET\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            f"Theoretical expected : "
            f"{expected_average:.6f}\n"
        )

        file.write(
            f"Random strategy      : "
            f"{random_average:.6f}\n"
        )

        file.write(
            f"Weighted strategy    : "
            f"{weighted_average:.6f}\n\n"
        )

        file.write(
            "HEAD-TO-HEAD RESULTS\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            f"Random better   : "
            f"{results['random_wins']:,}\n"
        )

        file.write(
            f"Weighted better : "
            f"{results['weighted_wins']:,}\n"
        )

        file.write(
            f"Ties            : "
            f"{results['ties']:,}\n\n"
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

            random_count = (
                results[
                    "random_results"
                ][matches]
            )

            weighted_count = (
                results[
                    "weighted_results"
                ][matches]
            )

            file.write(
                f"{matches} matches\n"
            )

            file.write(
                f"  Random     : "
                f"{random_count:,} "
                f"("
                f"{random_count / SIMULATIONS:.8f}"
                f")\n"
            )

            file.write(
                f"  Weighted   : "
                f"{weighted_count:,} "
                f"("
                f"{weighted_count / SIMULATIONS:.8f}"
                f")\n"
            )

            file.write(
                f"  Theoretical: "
                f"{theoretical[matches]:.8f}"
                f"\n\n"
            )

        file.write(
            "INTERPRETATION\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            "If the winning draw is fair and "
            "uniform, historical-frequency "
            "weighting should not provide a "
            "persistent advantage over a pure "
            "random ticket.\n"
        )

        file.write(
            "Any small difference observed in "
            "a finite simulation may be caused "
            "by random sampling variation.\n"
        )


def print_results(
    results,
    theoretical,
):
    print()
    print("=" * 60)
    print(
        "MONTE CARLO RESULTS"
    )
    print("=" * 60)

    print()
    print(
        f"Simulations: "
        f"{SIMULATIONS:,}"
    )

    print()

    print(
        f"{'Matches':>7} "
        f"{'Random':>12} "
        f"{'Weighted':>12} "
        f"{'Theory':>12}"
    )

    for matches in range(
        0,
        PICKS_PER_TICKET + 1,
    ):

        random_count = (
            results[
                "random_results"
            ][matches]
        )

        weighted_count = (
            results[
                "weighted_results"
            ][matches]
        )

        print(
            f"{matches:>7} "
            f"{random_count:>12,} "
            f"{weighted_count:>12,} "
            f"{theoretical[matches]:>12.8f}"
        )

    print()

    random_average = (
        results[
            "random_total_matches"
        ]
        / SIMULATIONS
    )

    weighted_average = (
        results[
            "weighted_total_matches"
        ]
        / SIMULATIONS
    )

    print(
        f"Average matches - Random   : "
        f"{random_average:.6f}"
    )

    print(
        f"Average matches - Weighted : "
        f"{weighted_average:.6f}"
    )

    print()

    print(
        f"Random better   : "
        f"{results['random_wins']:,}"
    )

    print(
        f"Weighted better : "
        f"{results['weighted_wins']:,}"
    )

    print(
        f"Ties            : "
        f"{results['ties']:,}"
    )


def main():
    csv_file, results_dir = (
        get_project_paths()
    )

    print()
    print("=" * 60)
    print(
        "Singapore TOTO 6/49 "
        "Monte Carlo Experiment"
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

    frequency = (
        calculate_historical_frequency(
            records
        )
    )

    print(
        f"Simulation runs: "
        f"{SIMULATIONS:,}"
    )

    print()
    print(
        "[START] Running simulation..."
    )

    results = run_simulation(
        frequency
    )

    theoretical = (
        calculate_theoretical_match_probabilities()
    )

    output_csv = (
        results_dir
        / "monte_carlo_results.csv"
    )

    output_summary = (
        results_dir
        / "monte_carlo_summary.txt"
    )

    save_results(
        results,
        theoretical,
        output_csv,
    )

    save_summary(
        results,
        theoretical,
        output_summary,
    )

    print_results(
        results,
        theoretical,
    )

    print()
    print("=" * 60)
    print(
        "OUTPUT FILES"
    )
    print("=" * 60)

    print(
        f"[FILE] {output_csv}"
    )

    print(
        f"[FILE] {output_summary}"
    )

    print()
    print(
        "[DONE] Monte Carlo experiment complete."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

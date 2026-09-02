import csv
import random
from collections import Counter
from itertools import combinations
from pathlib import Path


# ============================================================
# Singapore TOTO 6/49
# Final SGD18 Coverage Ticket Generator
#
# Budget:
#   SGD 18
#
# Tickets:
#   18 x SGD1
#
# Design principle:
#   Phase 1 found no reproducible predictive advantage from:
#
#   - historical frequency
#   - pair frequency
#   - rolling frequency
#   - combination structure
#
# Therefore the final experiment does NOT attempt to predict
# "hot" or "likely" numbers.
#
# Instead, the 18-ticket portfolio is designed to:
#
#   1. Cover numbers 1-49 as evenly as possible.
#   2. Minimize repeated number-pairs across tickets.
#   3. Avoid excessive overlap between tickets.
#   4. Avoid unnecessarily extreme odd/even or low/high
#      concentration across the portfolio.
#   5. Remain completely reproducible using a fixed seed.
#
# Important:
#   This design does NOT increase the probability of any
#   individual 6-number combination being drawn.
# ============================================================


BALL_MIN = 1
BALL_MAX = 49

TICKET_COUNT = 18
NUMBERS_PER_TICKET = 6

TOTAL_SLOTS = (
    TICKET_COUNT
    * NUMBERS_PER_TICKET
)

RANDOM_SEED = 20260902

SEARCH_ITERATIONS = 200_000


def get_output_directory():
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    script_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return script_dir


def build_target_usage(rng):
    """
    18 tickets x 6 numbers = 108 total number slots.

    49 numbers x 2 appearances = 98 slots.

    Therefore:
        39 numbers appear exactly 2 times
        10 numbers appear exactly 3 times

    The ten numbers receiving the third appearance are selected
    only from the fixed random seed, NOT historical frequency.
    """

    numbers = list(
        range(
            BALL_MIN,
            BALL_MAX + 1
        )
    )

    extra_numbers = set(
        rng.sample(
            numbers,
            TOTAL_SLOTS
            - (BALL_MAX * 2),
        )
    )

    target_usage = {}

    for number in numbers:
        target_usage[number] = (
            3
            if number in extra_numbers
            else 2
        )

    return target_usage


def ticket_odd_count(ticket):
    return sum(
        1
        for number in ticket
        if number % 2 == 1
    )


def ticket_low_count(ticket):
    """
    Low numbers:
        1-24

    High numbers:
        25-49
    """

    return sum(
        1
        for number in ticket
        if number <= 24
    )


def max_ticket_overlap(tickets):
    maximum = 0

    for ticket_a, ticket_b in combinations(
        tickets,
        2,
    ):
        overlap = len(
            set(ticket_a)
            & set(ticket_b)
        )

        maximum = max(
            maximum,
            overlap,
        )

    return maximum


def repeated_pair_count(tickets):
    pair_counter = Counter()

    for ticket in tickets:
        for pair in combinations(
            ticket,
            2,
        ):
            pair_counter[pair] += 1

    return sum(
        count - 1
        for count in pair_counter.values()
        if count > 1
    )


def ticket_shape_penalty(ticket):
    """
    This is NOT a prediction rule.

    It merely discourages highly concentrated portfolio
    construction.

    Preferred:
        odd count 2-4
        low count 2-4
    """

    odd_count = ticket_odd_count(
        ticket
    )

    low_count = ticket_low_count(
        ticket
    )

    penalty = 0

    if odd_count < 2:
        penalty += (
            2 - odd_count
        ) * 3

    if odd_count > 4:
        penalty += (
            odd_count - 4
        ) * 3

    if low_count < 2:
        penalty += (
            2 - low_count
        ) * 3

    if low_count > 4:
        penalty += (
            low_count - 4
        ) * 3

    return penalty


def portfolio_score(tickets):
    """
    Lower score is better.

    Priority:
        1. Repeated pairs
        2. Large ticket-to-ticket overlap
        3. Extreme ticket shape

    Number usage balance is handled separately and is always
    preserved by the generator.
    """

    repeated_pairs = (
        repeated_pair_count(
            tickets
        )
    )

    maximum_overlap = (
        max_ticket_overlap(
            tickets
        )
    )

    shape_penalty = sum(
        ticket_shape_penalty(
            ticket
        )
        for ticket in tickets
    )

    return (
        repeated_pairs * 1000
        + max(
            0,
            maximum_overlap - 1
        ) * 500
        + shape_penalty
    )


def generate_initial_portfolio(
    rng,
    target_usage,
):
    """
    Create a portfolio while respecting exact target number
    usage counts.
    """

    pool = []

    for number, count in (
        target_usage.items()
    ):
        pool.extend(
            [number] * count
        )

    for _ in range(10_000):

        rng.shuffle(pool)

        tickets = []

        valid = True

        for index in range(
            TICKET_COUNT
        ):

            ticket = sorted(
                pool[
                    index
                    * NUMBERS_PER_TICKET:
                    (index + 1)
                    * NUMBERS_PER_TICKET
                ]
            )

            if len(set(ticket)) != (
                NUMBERS_PER_TICKET
            ):
                valid = False
                break

            tickets.append(
                ticket
            )

        if valid:
            return tickets

    raise RuntimeError(
        "Could not create valid initial portfolio."
    )


def optimize_portfolio(
    rng,
    initial_tickets,
):
    """
    Random swap optimization.

    Swapping numbers between tickets preserves the exact
    number-usage counts across the full 18-ticket portfolio.
    """

    best_tickets = [
        ticket[:]
        for ticket in initial_tickets
    ]

    best_score = (
        portfolio_score(
            best_tickets
        )
    )

    current_tickets = [
        ticket[:]
        for ticket in initial_tickets
    ]

    current_score = best_score

    for iteration in range(
        1,
        SEARCH_ITERATIONS + 1,
    ):

        ticket_a_index, (
            ticket_b_index
        ) = rng.sample(
            range(
                TICKET_COUNT
            ),
            2,
        )

        ticket_a = (
            current_tickets[
                ticket_a_index
            ]
        )

        ticket_b = (
            current_tickets[
                ticket_b_index
            ]
        )

        position_a = rng.randrange(
            NUMBERS_PER_TICKET
        )

        position_b = rng.randrange(
            NUMBERS_PER_TICKET
        )

        number_a = ticket_a[
            position_a
        ]

        number_b = ticket_b[
            position_b
        ]

        if number_a == number_b:
            continue

        if number_b in ticket_a:
            continue

        if number_a in ticket_b:
            continue

        new_ticket_a = (
            ticket_a[:]
        )

        new_ticket_b = (
            ticket_b[:]
        )

        new_ticket_a[
            position_a
        ] = number_b

        new_ticket_b[
            position_b
        ] = number_a

        new_ticket_a.sort()
        new_ticket_b.sort()

        old_ticket_a = (
            current_tickets[
                ticket_a_index
            ]
        )

        old_ticket_b = (
            current_tickets[
                ticket_b_index
            ]
        )

        current_tickets[
            ticket_a_index
        ] = new_ticket_a

        current_tickets[
            ticket_b_index
        ] = new_ticket_b

        new_score = (
            portfolio_score(
                current_tickets
            )
        )

        if new_score <= current_score:
            current_score = (
                new_score
            )

            if new_score < best_score:
                best_score = (
                    new_score
                )

                best_tickets = [
                    ticket[:]
                    for ticket
                    in current_tickets
                ]

        else:
            current_tickets[
                ticket_a_index
            ] = old_ticket_a

            current_tickets[
                ticket_b_index
            ] = old_ticket_b

        if iteration % 20_000 == 0:
            print(
                f"[PROGRESS] "
                f"{iteration:,} / "
                f"{SEARCH_ITERATIONS:,} "
                f"| best score = "
                f"{best_score}"
            )

        if best_score == 0:
            break

    return (
        best_tickets,
        best_score,
    )


def verify_portfolio(
    tickets,
    target_usage,
):
    if len(tickets) != TICKET_COUNT:
        raise ValueError(
            "Incorrect ticket count."
        )

    usage = Counter()

    for ticket in tickets:

        if len(ticket) != (
            NUMBERS_PER_TICKET
        ):
            raise ValueError(
                "Incorrect numbers per ticket."
            )

        if len(set(ticket)) != (
            NUMBERS_PER_TICKET
        ):
            raise ValueError(
                "Duplicate number within a ticket."
            )

        for number in ticket:

            if not (
                BALL_MIN
                <= number
                <= BALL_MAX
            ):
                raise ValueError(
                    f"Invalid number: {number}"
                )

        usage.update(
            ticket
        )

    for number in range(
        BALL_MIN,
        BALL_MAX + 1,
    ):

        if usage[number] != (
            target_usage[number]
        ):
            raise ValueError(
                f"Usage mismatch for "
                f"number {number}: "
                f"{usage[number]} "
                f"!= "
                f"{target_usage[number]}"
            )

    return usage


def save_tickets_csv(
    tickets,
    output_file,
):
    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "ticket",
                "n1",
                "n2",
                "n3",
                "n4",
                "n5",
                "n6",
                "odd_count",
                "even_count",
                "low_count",
                "high_count",
                "sum",
            ]
        )

        for index, ticket in enumerate(
            tickets,
            start=1,
        ):

            odd_count = (
                ticket_odd_count(
                    ticket
                )
            )

            low_count = (
                ticket_low_count(
                    ticket
                )
            )

            writer.writerow(
                [
                    index,
                    *ticket,
                    odd_count,
                    NUMBERS_PER_TICKET
                    - odd_count,
                    low_count,
                    NUMBERS_PER_TICKET
                    - low_count,
                    sum(ticket),
                ]
            )


def save_summary(
    tickets,
    usage,
    target_usage,
    score,
    output_file,
):
    repeated_pairs = (
        repeated_pair_count(
            tickets
        )
    )

    maximum_overlap = (
        max_ticket_overlap(
            tickets
        )
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Singapore TOTO 6/49\n"
        )

        file.write(
            "Final SGD18 Coverage Portfolio\n"
        )

        file.write(
            "=" * 70
            + "\n\n"
        )

        file.write(
            f"Budget            : SGD 18\n"
        )

        file.write(
            f"Tickets           : "
            f"{TICKET_COUNT}\n"
        )

        file.write(
            f"Numbers per ticket: "
            f"{NUMBERS_PER_TICKET}\n"
        )

        file.write(
            f"Total slots       : "
            f"{TOTAL_SLOTS}\n"
        )

        file.write(
            f"Random seed       : "
            f"{RANDOM_SEED}\n"
        )

        file.write(
            f"Search iterations : "
            f"{SEARCH_ITERATIONS:,}\n\n"
        )

        file.write(
            "DESIGN PRINCIPLE\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        file.write(
            "No historical number, pair, rolling-frequency, "
            "or combination-structure signal demonstrated a "
            "reproducible predictive advantage in Phase 1.\n\n"
        )

        file.write(
            "Therefore these tickets are designed for portfolio "
            "coverage and low redundancy, not prediction.\n\n"
        )

        file.write(
            "PORTFOLIO QUALITY\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        file.write(
            f"Optimization score   : "
            f"{score}\n"
        )

        file.write(
            f"Repeated number pairs: "
            f"{repeated_pairs}\n"
        )

        file.write(
            f"Maximum overlap "
            f"between two tickets: "
            f"{maximum_overlap}\n\n"
        )

        file.write(
            "NUMBER USAGE\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        for number in range(
            BALL_MIN,
            BALL_MAX + 1,
        ):

            file.write(
                f"{number:>2}: "
                f"{usage[number]} "
                f"(target "
                f"{target_usage[number]})\n"
            )

        file.write("\n")

        file.write(
            "FINAL 18 TICKETS\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        for index, ticket in enumerate(
            tickets,
            start=1,
        ):

            file.write(
                f"{index:>2}: "
                + " ".join(
                    f"{number:02d}"
                    for number in ticket
                )
                + "\n"
            )

        file.write("\n")

        file.write(
            "IMPORTANT\n"
        )

        file.write(
            "-" * 70
            + "\n"
        )

        file.write(
            "This portfolio does not change the probability "
            "that any particular six-number combination is "
            "drawn.\n"
        )

        file.write(
            "Its purpose is to make the fixed SGD18 experiment "
            "transparent, reproducible, and less internally "
            "redundant.\n"
        )


def print_portfolio(
    tickets,
    usage,
    score,
):
    print()
    print("=" * 70)
    print(
        "FINAL SGD18 COVERAGE PORTFOLIO"
    )
    print("=" * 70)

    for index, ticket in enumerate(
        tickets,
        start=1,
    ):

        print(
            f"Ticket {index:>2}: "
            + " ".join(
                f"{number:02d}"
                for number in ticket
            )
        )

    print()
    print(
        f"Optimization score   : "
        f"{score}"
    )

    print(
        f"Repeated number pairs: "
        f"{repeated_pair_count(tickets)}"
    )

    print(
        f"Maximum ticket overlap: "
        f"{max_ticket_overlap(tickets)}"
    )

    usage_values = [
        usage[number]
        for number in range(
            BALL_MIN,
            BALL_MAX + 1,
        )
    ]

    print(
        f"Minimum number usage : "
        f"{min(usage_values)}"
    )

    print(
        f"Maximum number usage : "
        f"{max(usage_values)}"
    )


def main():
    output_dir = (
        get_output_directory()
    )

    rng = random.Random(
        RANDOM_SEED
    )

    print()
    print("=" * 70)
    print(
        "Singapore TOTO 6/49 "
        "Final SGD18 Ticket Generator"
    )
    print("=" * 70)

    print(
        f"Tickets     : "
        f"{TICKET_COUNT}"
    )

    print(
        f"Total slots : "
        f"{TOTAL_SLOTS}"
    )

    print(
        f"Seed        : "
        f"{RANDOM_SEED}"
    )

    print()
    print(
        "[START] Building balanced number usage..."
    )

    target_usage = (
        build_target_usage(
            rng
        )
    )

    print(
        "[START] Creating initial portfolio..."
    )

    initial_tickets = (
        generate_initial_portfolio(
            rng,
            target_usage,
        )
    )

    print(
        "[START] Optimizing ticket overlap..."
    )

    (
        final_tickets,
        final_score,
    ) = optimize_portfolio(
        rng,
        initial_tickets,
    )

    usage = verify_portfolio(
        final_tickets,
        target_usage,
    )

    ticket_file = (
        output_dir
        / "final_18_tickets.csv"
    )

    summary_file = (
        output_dir
        / "final_18_tickets_summary.txt"
    )

    save_tickets_csv(
        final_tickets,
        ticket_file,
    )

    save_summary(
        final_tickets,
        usage,
        target_usage,
        final_score,
        summary_file,
    )

    print_portfolio(
        final_tickets,
        usage,
        final_score,
    )

    print()
    print("=" * 70)
    print(
        "OUTPUT FILES"
    )
    print("=" * 70)

    print(
        f"[FILE] {ticket_file}"
    )

    print(
        f"[FILE] {summary_file}"
    )

    print()
    print(
        "[DONE] Final SGD18 portfolio generated."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()

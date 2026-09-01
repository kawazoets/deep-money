import base64
import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


# ============================================================
# Singapore TOTO 6/49 Historical Results Collector
#
# Fixed research window:
#   First 6/49 draw : 2995 (09 Oct 2014)
#   Cut-off draw     : 4213 (31 Aug 2026)
#
# Expected total:
#   4213 - 2995 + 1 = 1,219 draws
# ============================================================


BASE_URL = (
    "https://www.singaporepools.com.sg/"
    "en/product/sr/Pages/toto_results.aspx"
)

FIRST_DRAW = 2995
LAST_DRAW = 4213

REQUEST_DELAY_SECONDS = 1.0
MAX_RETRIES = 3
CHECKPOINT_INTERVAL = 50


@dataclass
class TotoDraw:
    draw_no: int
    draw_date: str
    n1: int
    n2: int
    n3: int
    n4: int
    n5: int
    n6: int
    additional: int

    def to_row(self) -> list:
        return [
            self.draw_no,
            self.draw_date,
            self.n1,
            self.n2,
            self.n3,
            self.n4,
            self.n5,
            self.n6,
            self.additional,
        ]


def get_output_file() -> Path:
    """
    When the script is inside:
        Special_01_Singapore_TOTO/scripts/
    save into:
        Special_01_Singapore_TOTO/data/

    When the script is downloaded and run directly from Downloads,
    save the CSV beside the downloaded script.
    """

    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    if script_dir.name.lower() == "scripts":
        output_dir = script_dir.parent / "data"
    else:
        output_dir = script_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir / "toto_draws_6of49.csv"


OUTPUT_FILE = get_output_file()


def build_draw_url(draw_no: int) -> str:
    """
    Singapore Pools historical draw URLs use a Base64 encoded
    query string containing:

        DrawNumber=<draw_no>
    """

    query_text = f"DrawNumber={draw_no}"

    encoded_query = base64.b64encode(
        query_text.encode("utf-8")
    ).decode("utf-8")

    return f"{BASE_URL}?sppl={encoded_query}"


def fetch_page(
    session: requests.Session,
    draw_no: int,
) -> Optional[str]:
    """
    Download one historical draw page.

    Retries temporary request failures up to MAX_RETRIES times.
    """

    url = build_draw_url(draw_no)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                url,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as exc:
            print(
                f"[WARN] Draw {draw_no} request failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {exc}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)

    return None


def parse_draw_page(
    html: str,
) -> Optional[TotoDraw]:
    """
    Parse one Singapore Pools TOTO result page.

    Extract:
        draw number
        draw date
        six winning numbers
        additional number
    """

    soup = BeautifulSoup(html, "html.parser")

    text = " ".join(soup.stripped_strings)

    # --------------------------------------------------------
    # Draw number
    # --------------------------------------------------------

    draw_match = re.search(
        r"Draw\s*No\.?\s*(\d+)",
        text,
        re.IGNORECASE,
    )

    if not draw_match:
        draw_match = re.search(
            r"Draw\s*(\d+)",
            text,
            re.IGNORECASE,
        )

    if not draw_match:
        return None

    draw_no = int(draw_match.group(1))

    # --------------------------------------------------------
    # Draw date
    # --------------------------------------------------------

    date_match = re.search(
        r"(\d{1,2}\s+"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\s+\d{4})",
        text,
        re.IGNORECASE,
    )

    if not date_match:
        return None

    draw_date = date_match.group(1)

    # --------------------------------------------------------
    # Winning numbers
    #
    # Singapore Pools page normally contains the phrase
    # "Winning Numbers".
    # --------------------------------------------------------

    winning_match = re.search(
        r"Winning\s+Numbers"
        r".*?"
        r"\b(\d{1,2})\b"
        r".*?"
        r"\b(\d{1,2})\b"
        r".*?"
        r"\b(\d{1,2})\b"
        r".*?"
        r"\b(\d{1,2})\b"
        r".*?"
        r"\b(\d{1,2})\b"
        r".*?"
        r"\b(\d{1,2})\b"
        r".*?"
        r"Additional",
        text,
        re.IGNORECASE,
    )

    if not winning_match:
        return None

    winning_numbers = [
        int(winning_match.group(i))
        for i in range(1, 7)
    ]

    # --------------------------------------------------------
    # Additional number
    # --------------------------------------------------------

    additional_match = re.search(
        r"Additional"
        r"(?:\s+Number)?"
        r".*?"
        r"\b(\d{1,2})\b",
        text,
        re.IGNORECASE,
    )

    if not additional_match:
        return None

    additional = int(additional_match.group(1))

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if len(winning_numbers) != 6:
        return None

    if len(set(winning_numbers)) != 6:
        return None

    if any(
        number < 1 or number > 49
        for number in winning_numbers
    ):
        return None

    if additional < 1 or additional > 49:
        return None

    if additional in winning_numbers:
        return None

    winning_numbers.sort()

    return TotoDraw(
        draw_no=draw_no,
        draw_date=draw_date,
        n1=winning_numbers[0],
        n2=winning_numbers[1],
        n3=winning_numbers[2],
        n4=winning_numbers[3],
        n5=winning_numbers[4],
        n6=winning_numbers[5],
        additional=additional,
    )


def save_csv(
    records: list[TotoDraw],
    output_file: Path,
) -> None:
    """
    Save all currently collected records.

    The file is overwritten each time so that checkpoints
    always contain a clean complete dataset up to that point.
    """

    records = sorted(
        records,
        key=lambda record: record.draw_no,
    )

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
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
        )

        for record in records:
            writer.writerow(record.to_row())


def collect_draws(
    start_draw: int,
    end_draw: int,
) -> tuple[list[TotoDraw], list[int], list[int]]:
    """
    Collect a continuous range of draw numbers.

    Returns:
        records
        failed draws
        mismatched draws
    """

    records: list[TotoDraw] = []
    failed_draws: list[int] = []
    mismatched_draws: list[int] = []

    session = requests.Session()

    total_requested = end_draw - start_draw + 1

    print()
    print("=" * 60)
    print("Singapore TOTO 6/49 Historical Data Collection")
    print("=" * 60)
    print(f"Start draw : {start_draw}")
    print(f"End draw   : {end_draw}")
    print(f"Requested  : {total_requested}")
    print(f"Output     : {OUTPUT_FILE}")
    print("=" * 60)
    print()

    for index, draw_no in enumerate(
        range(start_draw, end_draw + 1),
        start=1,
    ):
        print(
            f"[INFO] "
            f"{index}/{total_requested} "
            f"Fetching draw {draw_no}"
        )

        html = fetch_page(
            session,
            draw_no,
        )

        if html is None:
            print(
                f"[ERROR] Could not download draw {draw_no}"
            )

            failed_draws.append(draw_no)

            continue

        record = parse_draw_page(html)

        if record is None:
            print(
                f"[ERROR] Could not parse draw {draw_no}"
            )

            failed_draws.append(draw_no)

            continue

        # ----------------------------------------------------
        # Critical validation:
        #
        # The returned draw number MUST equal the requested
        # draw number.
        #
        # This prevents a failed historical query from silently
        # returning the current/latest result page.
        # ----------------------------------------------------

        if record.draw_no != draw_no:
            print(
                f"[ERROR] Requested draw {draw_no}, "
                f"but received draw {record.draw_no}"
            )

            mismatched_draws.append(draw_no)

            continue

        records.append(record)

        numbers_text = ", ".join(
            str(number)
            for number in [
                record.n1,
                record.n2,
                record.n3,
                record.n4,
                record.n5,
                record.n6,
            ]
        )

        print(
            f"[OK] {record.draw_no} | "
            f"{record.draw_date} | "
            f"{numbers_text} | "
            f"Additional {record.additional}"
        )

        # ----------------------------------------------------
        # Checkpoint
        # ----------------------------------------------------

        if len(records) % CHECKPOINT_INTERVAL == 0:
            save_csv(
                records,
                OUTPUT_FILE,
            )

            print(
                f"[CHECKPOINT] "
                f"Saved {len(records)} draws"
            )

        time.sleep(REQUEST_DELAY_SECONDS)

    session.close()

    return (
        records,
        failed_draws,
        mismatched_draws,
    )


def validate_final_dataset(
    records: list[TotoDraw],
    start_draw: int,
    end_draw: int,
) -> None:
    """
    Basic structural validation after collection.
    """

    expected_count = end_draw - start_draw + 1
    actual_count = len(records)

    draw_numbers = [
        record.draw_no
        for record in records
    ]

    duplicate_count = (
        len(draw_numbers)
        - len(set(draw_numbers))
    )

    missing_draws = sorted(
        set(range(start_draw, end_draw + 1))
        - set(draw_numbers)
    )

    print()
    print("=" * 60)
    print("FINAL DATASET VALIDATION")
    print("=" * 60)

    print(f"Expected rows : {expected_count}")
    print(f"Actual rows   : {actual_count}")
    print(f"Duplicates    : {duplicate_count}")
    print(f"Missing draws : {len(missing_draws)}")

    if missing_draws:
        print(
            "Missing draw numbers: "
            + ", ".join(
                str(draw_no)
                for draw_no in missing_draws
            )
        )

    if (
        actual_count == expected_count
        and duplicate_count == 0
        and not missing_draws
    ):
        print()
        print(
            "[PASS] Basic dataset structure is complete."
        )
    else:
        print()
        print(
            "[WARNING] Dataset requires further checking."
        )

    print("=" * 60)


def main() -> None:
    records, failed_draws, mismatched_draws = (
        collect_draws(
            FIRST_DRAW,
            LAST_DRAW,
        )
    )

    # Always save whatever was successfully collected,
    # including partial data if some requests failed.
    save_csv(
        records,
        OUTPUT_FILE,
    )

    expected_count = LAST_DRAW - FIRST_DRAW + 1

    print()
    print("=" * 60)
    print("COLLECTION SUMMARY")
    print("=" * 60)

    print(f"Requested  : {expected_count}")
    print(f"Collected  : {len(records)}")
    print(f"Failed     : {len(failed_draws)}")
    print(f"Mismatch   : {len(mismatched_draws)}")

    if failed_draws:
        print(
            "Failed draws: "
            + ", ".join(
                str(draw_no)
                for draw_no in failed_draws
            )
        )

    if mismatched_draws:
        print(
            "Mismatched draws: "
            + ", ".join(
                str(draw_no)
                for draw_no in mismatched_draws
            )
        )

    print()
    print(f"[FILE] {OUTPUT_FILE}")

    print("=" * 60)

    validate_final_dataset(
        records,
        FIRST_DRAW,
        LAST_DRAW,
    )


if __name__ == "__main__":
    main()

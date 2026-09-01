"""
Deep Money Special 01
Singapore TOTO — Historical Results Collector

Purpose
-------
Collect Singapore TOTO historical draw results and save them
as a reproducible CSV dataset for statistical analysis.

Current TOTO format:
- 6 Winning Numbers
- 1 Additional Number
- Numbers are drawn from 1 to 49

The current 6/49 format was introduced in October 2014.

Primary source:
Singapore Pools

Project:
Deep Money Special 01
Singapore TOTO — One Million Simulations
"""

from __future__ import annotations

import base64
import csv
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


# ============================================================
# Configuration
# ============================================================

BASE_URL = (
    "https://www.singaporepools.com.sg/"
    "en/product/sr/Pages/toto_results.aspx"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "toto_draws_6of49.csv"
)

REQUEST_DELAY_SECONDS = 1.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; DeepMoneyResearch/1.0; "
        "+https://github.com/)"
    )
}


# ============================================================
# Data model
# ============================================================

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


# ============================================================
# URL handling
# ============================================================

def build_draw_url(draw_no: int) -> str:
    """
    Build the Singapore Pools historical TOTO result URL.

    Singapore Pools uses a Base64-encoded query value
    representing:

        DrawNumber=<draw number>

    Example:
        DrawNumber=4183
        -> RHJhd051bWJlcj00MTgz
    """

    query_text = f"DrawNumber={draw_no}"

    encoded_query = base64.b64encode(
        query_text.encode("utf-8")
    ).decode("utf-8")

    return f"{BASE_URL}?sppl={encoded_query}"


# ============================================================
# Download
# ============================================================

def fetch_page(draw_no: int) -> Optional[str]:
    """
    Download one Singapore Pools TOTO result page.

    Returns
    -------
    str
        HTML content if successful.

    None
        If the page cannot be retrieved.
    """

    url = build_draw_url(draw_no)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as exc:
        print(f"[ERROR] Draw {draw_no}: {exc}")
        return None


# ============================================================
# Parsing
# ============================================================

def parse_draw_page(html: str) -> Optional[TotoDraw]:
    """
    Extract draw number, date, six winning numbers,
    and the Additional Number from a TOTO result page.

    The parser validates all extracted values.
    If the expected structure is not found, None is returned.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    text = " ".join(
        soup.stripped_strings
    )

    # --------------------------------------------------------
    # Draw number
    # --------------------------------------------------------

    draw_match = re.search(
        r"Draw\s*No\.?\s*(\d+)",
        text,
        flags=re.IGNORECASE,
    )

    if not draw_match:
        return None

    draw_no = int(
        draw_match.group(1)
    )

    # --------------------------------------------------------
    # Draw date
    # --------------------------------------------------------

    date_match = re.search(
        r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+"
        r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})",
        text,
    )

    if not date_match:
        return None

    draw_date = date_match.group(2)

    # --------------------------------------------------------
    # Winning numbers
    # --------------------------------------------------------

    winning_match = re.search(
        r"Winning Numbers\s+"
        r"(\d{1,2})\s+"
        r"(\d{1,2})\s+"
        r"(\d{1,2})\s+"
        r"(\d{1,2})\s+"
        r"(\d{1,2})\s+"
        r"(\d{1,2})",
        text,
        flags=re.IGNORECASE,
    )

    if not winning_match:
        return None

    winning_numbers = [
        int(value)
        for value in winning_match.groups()
    ]

    # --------------------------------------------------------
    # Additional number
    # --------------------------------------------------------

    additional_match = re.search(
        r"Additional Number\s+(\d{1,2})",
        text,
        flags=re.IGNORECASE,
    )

    if not additional_match:
        return None

    additional = int(
        additional_match.group(1)
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if len(set(winning_numbers)) != 6:
        return None

    if not all(
        1 <= number <= 49
        for number in winning_numbers
    ):
        return None

    if not 1 <= additional <= 49:
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


# ============================================================
# Collection
# ============================================================

def collect_draws(
    start_draw: int,
    end_draw: int,
) -> list[TotoDraw]:
    """
    Collect a range of TOTO draws.

    Parameters
    ----------
    start_draw:
        First draw number to request.

    end_draw:
        Last draw number to request, inclusive.
    """

    records: list[TotoDraw] = []

    for draw_no in range(
        start_draw,
        end_draw + 1,
    ):

        print(
            f"[INFO] Fetching draw {draw_no}"
        )

        html = fetch_page(draw_no)

        if html is None:
            continue

        record = parse_draw_page(html)

        if record is None:
            print(
                f"[WARNING] Could not parse draw {draw_no}"
            )
            continue

        # ----------------------------------------------------
        # Critical validation:
        # requested draw must equal returned draw
        # ----------------------------------------------------

        if record.draw_no != draw_no:
            print(
                f"[ERROR] Requested draw {draw_no}, "
                f"but received draw {record.draw_no}"
            )
            continue

        records.append(record)

        print(
            f"[OK] {record.draw_no} | "
            f"{record.draw_date} | "
            f"{record.n1}, {record.n2}, {record.n3}, "
            f"{record.n4}, {record.n5}, {record.n6} | "
            f"Additional {record.additional}"
        )

        time.sleep(
            REQUEST_DELAY_SECONDS
        )

    return records


# ============================================================
# CSV output
# ============================================================

def save_csv(
    records: list[TotoDraw],
) -> None:
    """
    Save collected draw records to CSV.
    """

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
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

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in records:
            writer.writerow(
                asdict(record)
            )

    print()
    print(
        f"[DONE] Saved {len(records)} draws"
    )
    print(
        f"[FILE] {OUTPUT_FILE}"
    )


# ============================================================
# Main
# ============================================================

def main() -> None:
    """
    Initial validation run.

    Only two historical draws are requested.

    Full historical collection should not begin until
    these results have been verified against the official
    Singapore Pools records.
    """

    TEST_START_DRAW = 4210
    TEST_END_DRAW = 4211

    records = collect_draws(
        TEST_START_DRAW,
        TEST_END_DRAW,
    )

    save_csv(records)


if __name__ == "__main__":
    main()

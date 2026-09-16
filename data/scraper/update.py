"""
Incremental Maharashtra mandi data updater.

Reads:
    data/raw/maharashtra_prices.csv

Finds the latest date already present in the CSV and fetches
only dates after that up to today.

New records are appended to the same raw CSV.

Usage:
    python scraper/update.py
"""

import csv
import os
import sys
from datetime import date, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data import (
    get_maharashtra_markets,
    fetch_daily_report,
    extract_rows,
) 

RAW_DIR = PROJECT_ROOT / "data" / "raw"

RAW_CSV = RAW_DIR / "maharashtra_prices.csv"



FIELDNAMES = [
    "report_date",
    "state_id",
    "state_name",
    "market_id",
    "market_name",
    "commodity_id",
    "commodity_name",
    "total_arrivals",
    "market_center",
    "arrivals",
    "unit_of_arrivals",
    "variety",
    "grade",
    "min_price",
    "max_price",
    "modal_price",
    "unit_of_price",
]




def get_latest_date(csv_path: Path) -> date:
    """
    Find the latest report_date already present
    in the raw CSV.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Raw CSV not found:\n{csv_path}"
        )

    latest_date = None

    with open(
        csv_path,
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            report_date = row.get("report_date")

            if not report_date:
                continue

            try:
                current_date = date.fromisoformat(
                    report_date
                )
            except ValueError:
                print(
                    f"Skipping invalid date: {report_date}"
                )
                continue

            if (
                latest_date is None
                or current_date > latest_date
            ):
                latest_date = current_date

    if latest_date is None:
        raise ValueError(
            "No valid report_date found in raw CSV."
        )

    return latest_date



def get_existing_dates(csv_path: Path) -> set[date]:
    """
    Return all dates already present in the raw CSV.

    This protects us from accidentally downloading
    duplicate dates.
    """

    existing_dates = set()

    with open(
        csv_path,
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            report_date = row.get("report_date")

            if not report_date:
                continue

            try:
                existing_dates.add(
                    date.fromisoformat(report_date)
                )
            except ValueError:
                continue

    return existing_dates




def append_rows(
    csv_path: Path,
    rows: list[dict],
) -> None:
    """
    Append scraped rows to the raw CSV.
    """

    if not rows:
        return

    file_exists = csv_path.exists()

    with open(
        csv_path,
        "a",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)

        f.flush()


def update_raw_data() -> None:

    print("=" * 70)
    print("MAHARASHTRA MANDI DATA INCREMENTAL UPDATE")
    print("=" * 70)

    # --------------------------------------------------------
    # Check raw CSV
    # --------------------------------------------------------

    if not RAW_CSV.exists():

        raise FileNotFoundError(
            f"\nRaw CSV does not exist:\n{RAW_CSV}\n\n"
            "Make sure maharashtra_prices.csv is inside:\n"
            "data/raw/"
        )

    print(f"\nRaw CSV:")
    print(RAW_CSV)


    existing_dates = get_existing_dates(
        RAW_CSV
    )

    latest_date = max(existing_dates)

    today = date.today()

    start_date = latest_date + timedelta(days=1)

    print(
        f"\nLatest date already present : {latest_date}"
    )

    print(
        f"Today's date                : {today}"
    )

    print(
        f"Update starts from          : {start_date}"
    )



    if start_date > today:

        print(
            "\nRaw dataset is already up to date."
        )

        return

 

    dates_to_fetch = []

    current = start_date

    while current <= today:

        if current not in existing_dates:
            dates_to_fetch.append(current)

        current += timedelta(days=1)

    if not dates_to_fetch:

        print(
            "\nNo missing dates found."
        )

        return

    print(
        f"\nDates that need to be fetched: "
        f"{len(dates_to_fetch)}"
    )

    print(
        f"First date: {dates_to_fetch[0]}"
    )

    print(
        f"Last date : {dates_to_fetch[-1]}"
    )



    print(
        "\nLoading Maharashtra market list..."
    )

    markets, market_ids = (
        get_maharashtra_markets()
    )

    print(
        f"Markets available: {len(market_ids)}"
    )

    total_new_rows = 0
    successful_dates = 0
    failed_dates = []

    for index, target_date in enumerate(
        dates_to_fetch,
        start=1,
    ):

        print(
            f"\n[{index}/{len(dates_to_fetch)}] "
            f"Fetching {target_date}..."
        )

        try:

            # Fetch API response
            data = fetch_daily_report(
                target_date,
                market_ids,
            )

            # Convert API response into CSV rows
            rows = extract_rows(
                data,
                target_date,
            )

            # Append to raw CSV
            append_rows(
                RAW_CSV,
                rows,
            )

            total_new_rows += len(rows)

            successful_dates += 1

            print(
                f"SUCCESS: {len(rows)} rows added"
            )

        except Exception as exc:

            failed_dates.append(
                target_date
            )

            print(
                f"FAILED: {target_date}"
            )

            print(
                f"Reason: {exc}"
            )

   

    print("\n" + "=" * 70)
    print("UPDATE COMPLETE")
    print("=" * 70)

    print(
        f"Successful dates : {successful_dates}"
    )

    print(
        f"Failed dates     : {len(failed_dates)}"
    )

    print(
        f"New rows added   : {total_new_rows}"
    )

    if failed_dates:

        print(
            "\nFailed dates:"
        )

        for failed_date in failed_dates:
            print(
                f"  {failed_date}"
            )

        print(
            "\nRun the updater again later to retry "
            "these dates."
        )

    else:

        print(
            "\nAll required dates were fetched."
        )

    print(
        f"\nUpdated raw file:\n{RAW_CSV}"
    )



if __name__ == "__main__":
    update_raw_data()
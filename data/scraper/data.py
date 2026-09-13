"""
Agmarknet historical mandi price scraper - Maharashtra

Based on reverse-engineered API calls from browser DevTools:
  - POST https://api.agmarknet.gov.in/v1/list-state
        body: {"stateIds": [20]}
        -> returns market/commodity list for the state
  - POST https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily
        body: {"date": "YYYY-MM-DD", "State": [20], "includeExcel": false,
               "marketIds": [...], "stateIds": [20], "title": "..."}
        -> returns daily price records

NOTE: This must be run from a machine with normal internet access.
It will NOT work from a sandboxed environment with a domain allowlist.
"""

import requests
import json
import csv
import time
from datetime import date, timedelta

BASE = "https://api.agmarknet.gov.in/v1"
MAHARASHTRA_STATE_ID = 20

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

# Status codes worth retrying (server-side / transient), vs. e.g. 400/404
# which won't fix themselves no matter how many times you ask.
RETRYABLE_STATUS_CODES = {500, 502, 503, 504, 408, 429}

MARKETS_CACHE_FILE = "markets_cache.json"


def post_with_retry(url, json_payload, headers, timeout=60, max_retries=6):
    """
    POST with exponential backoff. Retries on:
      - read/connect timeouts
      - connection errors (dropped connection, DNS blip, etc.)
      - transient server-side HTTP status codes (503, 502, 504, 429, ...)

    Does NOT retry on non-transient HTTP errors (e.g. 400 bad request,
    404 not found) - those will just fail the same way every time, so we
    raise immediately instead of wasting 6 retries on a dead end.
    """
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(url, json=json_payload, headers=headers, timeout=timeout)

            if resp.status_code in RETRYABLE_STATUS_CODES:
                wait = min(120, 2 ** attempt)
                print(f"  [retry] HTTP {resp.status_code} from server, "
                      f"retrying in {wait}s... (attempt {attempt}/{max_retries})")
                time.sleep(wait)
                continue

            resp.raise_for_status()  # raises on any other 4xx/5xx immediately
            return resp

        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError) as e:
            last_exc = e
            wait = min(120, 2 ** attempt)
            print(f"  [retry] {type(e).__name__}, retrying in {wait}s... "
                  f"(attempt {attempt}/{max_retries})")
            time.sleep(wait)

    raise RuntimeError(
        f"Gave up after {max_retries} retries on {url}"
    ) from last_exc


def get_maharashtra_markets(force_refresh=False):
    """
    Fetch the full market/commodity list for Maharashtra.

    This list barely ever changes, so by default it's cached to
    MARKETS_CACHE_FILE after the first successful fetch. Future runs load
    from that file instead of hitting list-state again - meaning a restart
    no longer depends on that endpoint being up at all (only the daily
    report endpoint does). Pass force_refresh=True to bypass the cache and
    re-fetch from the API (e.g. if you suspect the market list changed).
    """
    import os

    if not force_refresh and os.path.exists(MARKETS_CACHE_FILE):
        with open(MARKETS_CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
        markets = cached["markets"]
        market_ids = cached["market_ids"]
        print(f"Loaded {len(markets)} markets in Maharashtra from cache "
              f"({MARKETS_CACHE_FILE}).")
        return markets, market_ids

    url = f"{BASE}/list-state"
    payload = {"stateIds": [MAHARASHTRA_STATE_ID]}
    resp = post_with_retry(url, payload, HEADERS, timeout=30)
    data = resp.json()

    # data is a list like [{"state_id":20,"state_name":"Maharashtra","markets":[...]}]
    state_block = data[0]
    markets = state_block["markets"]
    market_ids = [m["id"] for m in markets]
    print(f"Found {len(markets)} markets in Maharashtra.")

    with open(MARKETS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"markets": markets, "market_ids": market_ids}, f)
    print(f"Cached market list to {MARKETS_CACHE_FILE} for future runs.")

    return markets, market_ids


def fetch_daily_report(target_date, market_ids, state_id=MAHARASHTRA_STATE_ID):
    """
    Fetch the daily price report for a single date.
    target_date: datetime.date object
    Returns the parsed JSON response (structure TBD - inspect first!)
    """
    url = f"{BASE}/prices-and-arrivals/market-report/daily"
    payload = {
        "date": target_date.strftime("%Y-%m-%d"),
        "State": [state_id],
        "includeExcel": False,
        "marketIds": market_ids,
        "stateIds": [state_id],
        "title": "Market Wise Daily Report",
    }
    resp = post_with_retry(url, payload, HEADERS, timeout=60)
    return resp.json()


def test_single_date():
    """Step 1: confirm the pipeline works end-to-end on ONE date, and print
    the raw response so we can see the actual key structure of the price
    records before writing the full parser."""
    markets, market_ids = get_maharashtra_markets()

    test_date = date(2024, 1, 15)  # pick any recent date to sanity check
    print(f"\nFetching report for {test_date} across {len(market_ids)} markets...")
    data = fetch_daily_report(test_date, market_ids)

    # Print a readable sample so we can see the real shape of the response
    print("\n--- RAW RESPONSE (first 2000 chars) ---")
    print(json.dumps(data, indent=2)[:2000])

    with open("sample_response.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nFull response saved to sample_response.json")

    rows = extract_rows(data, test_date)
    print(f"\nParsed {len(rows)} flattened rows. Sample:")
    if rows:
        print(json.dumps(rows[0], indent=2))


def scrape_date_range(start_date, end_date, market_ids, out_csv="maharashtra_prices.csv",
                       checkpoint_file="checkpoint.txt"):
    """
    Loops over a date range, fetches each day's report, and appends rows to
    CSV incrementally (so progress is never lost if the script crashes or
    is interrupted).

    Resume support: after each successful date, its ISO date string is
    written to `checkpoint_file`. On the next run, if that file exists,
    scraping resumes the day AFTER the last checkpointed date instead of
    starting over from `start_date`.
    """
    import os

    # --- Resume logic ---
    actual_start = start_date
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            last_done = f.read().strip()
        if last_done:
            last_date = date.fromisoformat(last_done)
            actual_start = last_date + timedelta(days=1)
            print(f"Resuming from checkpoint: last completed {last_date}, "
                  f"continuing from {actual_start}")

    if actual_start > end_date:
        print("Nothing to do - checkpoint is already past end_date.")
        return

    fieldnames = [
        "report_date", "state_id", "state_name", "market_id", "market_name",
        "commodity_id", "commodity_name", "total_arrivals", "market_center",
        "arrivals", "unit_of_arrivals", "variety", "grade", "min_price",
        "max_price", "modal_price", "unit_of_price",
    ]

    file_exists = os.path.exists(out_csv)
    csv_file = open(out_csv, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()

    # --- Progress tracking setup ---
    total_days = (end_date - actual_start).days + 1
    days_done = 0
    run_start_time = time.time()

    current = actual_start
    total_rows = 0
    try:
        while current <= end_date:
            try:
                data = fetch_daily_report(current, market_ids)
                rows = extract_rows(data, current)
                for row in rows:
                    writer.writerow(row)
                csv_file.flush()
                total_rows += len(rows)
                days_done += 1

                # --- Progress / ETA calculation ---
                elapsed = time.time() - run_start_time
                avg_per_day = elapsed / days_done
                remaining_days = total_days - days_done
                eta_seconds = avg_per_day * remaining_days
                pct = (days_done / total_days) * 100

                print(
                    f"{current}: {len(rows)} records "
                    f"(total so far: {total_rows} rows | "
                    f"{days_done}/{total_days} days, {pct:.1f}% | "
                    f"elapsed {_fmt_duration(elapsed)} | "
                    f"ETA {_fmt_duration(eta_seconds)})"
                )

                # checkpoint only after a successful write
                with open(checkpoint_file, "w") as cf:
                    cf.write(str(current))

            except Exception as e:
                # post_with_retry() already exhausted its own retries before
                # raising, so if we're here the day genuinely couldn't be
                # fetched after ~6 attempts with backoff. Log it and move on
                # rather than losing the whole run over one bad day.
                print(f"{current}: FAILED after retries ({e}) - will retry on next run")
                days_done += 1  # still counts toward progress display

            current += timedelta(days=1)
            time.sleep(0.5)  # be polite to the server
    finally:
        csv_file.close()

    total_elapsed = time.time() - run_start_time
    print(f"\nDone (or interrupted). {total_rows} rows written to {out_csv}")
    print(f"Total time this run: {_fmt_duration(total_elapsed)}")
    print(f"Checkpoint saved at {checkpoint_file} - re-run the script to resume.")


def _fmt_duration(seconds):
    """Format a seconds count as e.g. '1h 23m 05s' for readable progress output."""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def extract_rows(data, report_date):
    """
    Flattens the real Agmarknet response structure:

    data["states"] -> [ {stateId, stateName, markets: [
        {marketId, marketName, commodities: [
            {commodityId, commodityName, total_arrivals, data: [
                {marketCenter, arrivals, unitOfArrivals, variety, grade,
                 minimumPrice, maximumPrice, modalPrice, unitOfPrice}
            ]}
        ]}
    ]} ]

    Each innermost dict in "data" becomes one output row, tagged with
    state/market/commodity IDs and names plus the report date.
    """
    rows = []
    for state in data.get("states", []):
        state_id = state.get("stateId")
        state_name = state.get("stateName")
        for market in state.get("markets", []):
            market_id = market.get("marketId")
            market_name = market.get("marketName")
            for commodity in market.get("commodities", []):
                commodity_id = commodity.get("commodityId")
                commodity_name = commodity.get("commodityName")
                total_arrivals = commodity.get("total_arrivals")
                for rec in commodity.get("data", []):
                    row = {
                        "report_date": str(report_date),
                        "state_id": state_id,
                        "state_name": state_name,
                        "market_id": market_id,
                        "market_name": market_name,
                        "commodity_id": commodity_id,
                        "commodity_name": commodity_name,
                        "total_arrivals": total_arrivals,
                        "market_center": rec.get("marketCenter"),
                        "arrivals": rec.get("arrivals"),
                        "unit_of_arrivals": rec.get("unitOfArrivals"),
                        "variety": rec.get("variety"),
                        "grade": rec.get("grade"),
                        "min_price": rec.get("minimumPrice"),
                        "max_price": rec.get("maximumPrice"),
                        "modal_price": rec.get("modalPrice"),
                        "unit_of_price": rec.get("unitOfPrice"),
                    }
                    rows.append(row)
    return rows


def run_full_scrape():
    """
    Runs the complete pipeline: fetch market list once, then loop over
    every date from 2021-01-01 to today, flatten each day's response,
    and write everything to one CSV.
    """
    # The market list fetch itself now retries with backoff via
    # post_with_retry(), so a transient 503/timeout here no longer kills
    # the whole script before scraping even starts.
    markets, market_ids = get_maharashtra_markets()

    start_date = date(2021, 8, 3)
    end_date = date.today()

    scrape_date_range(start_date, end_date, market_ids)


if __name__ == "__main__":
    # Step 1 (already done - parsing confirmed working):
    # test_single_date()

    # Step 2: full 2021 -> today scrape, with incremental CSV writes and
    # resume-from-checkpoint support. Safe to Ctrl+C and re-run later;
    # it'll pick up right after the last completed date.
    run_full_scrape()
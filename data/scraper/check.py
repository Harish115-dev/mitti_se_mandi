"""
Coverage diagnostic for maharashtra_prices.csv

Run this after (or during) the scrape to see:
  - date range actually covered vs expected
  - which dates are missing entirely
  - how many unique markets/commodities showed up
  - total row count

Usage: python check_coverage.py
"""

import csv
from datetime import date, timedelta
from collections import defaultdict

CSV_FILE = "maharashtra_prices.csv"
EXPECTED_START = date(2021, 1, 1)
EXPECTED_END = date.today()

dates_seen = set()
markets_seen = set()
commodities_seen = set()
rows_per_date = defaultdict(int)
total_rows = 0

with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_rows += 1
        d = row["report_date"]
        dates_seen.add(d)
        rows_per_date[d] += 1
        markets_seen.add(row["market_id"])
        commodities_seen.add(row["commodity_name"])

print(f"Total rows: {total_rows}")
print(f"Unique dates with data: {len(dates_seen)}")
print(f"Unique markets seen: {len(markets_seen)} (expected 429)")
print(f"Unique commodities seen: {len(commodities_seen)}")

if dates_seen:
    min_date = min(dates_seen)
    max_date = max(dates_seen)
    print(f"Date range covered: {min_date} to {max_date}")

# Find missing dates in the expected range
expected_dates = set()
d = EXPECTED_START
while d <= EXPECTED_END:
    expected_dates.add(str(d))
    d += timedelta(days=1)

missing_dates = sorted(expected_dates - dates_seen)
print(f"\nMissing dates (no rows at all): {len(missing_dates)}")
if missing_dates:
    print("First 10 missing:", missing_dates[:10])
    print("Last 10 missing:", missing_dates[-10:])

# Dates with suspiciously few rows (possible partial failures)
low_count_dates = sorted(
    [(d, c) for d, c in rows_per_date.items() if c < 50],
    key=lambda x: x[0]
)
print(f"\nDates with under 50 rows (possibly incomplete fetch): {len(low_count_dates)}")
if low_count_dates:
    print("Examples:", low_count_dates[:10])
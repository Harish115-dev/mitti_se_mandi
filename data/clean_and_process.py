"""
Clean and prepare Maharashtra mandi data.

Input:
    data/raw/maharashtra_prices.csv

Output:
    data/processed/df_reliable.pkl

This script reproduces the main cleaning rules used in the
modeling workflow:
    1. Load raw data
    2. Parse dates
    3. Remove redundant market_center
    4. Normalize text fields
    5. Remove rows with missing prices
    6. Enforce min <= modal <= max
    7. Keep only Rs./Quintal
    8. Remove extreme modal-price outliers per commodity
    9. Keep market+commodity series with at least 365 rows
    10. Save reliable cleaned dataframe
"""

from pathlib import Path

import numpy as np
import pandas as pd



PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "maharashtra_prices.csv"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "df_reliable.pkl"
)



def clean_and_process(
    input_file: Path = RAW_FILE,
    output_file: Path = OUTPUT_FILE,
) -> pd.DataFrame:

    print("=" * 70)
    print("MAHARASHTRA MANDI DATA CLEANING")
    print("=" * 70)



    if not input_file.exists():
        raise FileNotFoundError(
            f"Raw CSV not found:\n{input_file}"
        )

    print(f"\nInput file:")
    print(input_file)

   
    print("\nLoading raw CSV...")

    df = pd.read_csv(
        input_file,
        low_memory=False,
    )

    print(
        f"Raw shape: {df.shape[0]:,} rows × "
        f"{df.shape[1]} columns"
    )

  

    df["report_date"] = pd.to_datetime(
        df["report_date"],
        errors="coerce",
    )

    invalid_dates = df["report_date"].isna().sum()

    if invalid_dates > 0:
        print(
            f"\nRemoving {invalid_dates:,} rows "
            "with invalid report_date..."
        )

        df = df.dropna(
            subset=["report_date"]
        )

 

    if "market_center" in df.columns:

        df = df.drop(
            columns=["market_center"]
        )

        print("\nDropped: market_center")

 

    text_columns = [
        "market_name",
        "commodity_name",
        "variety",
        "grade",
        "state_name",
        "unit_of_arrivals",
        "unit_of_price",
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True,
                )
                .str.strip()
            )

    print(
        "Normalized market/commodity/text fields."
    )



    price_columns = [
        "min_price",
        "max_price",
        "modal_price",
    ]

    for column in price_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )


    before = len(df)

    df = df.dropna(
        subset=[
            "min_price",
            "max_price",
            "modal_price",
        ]
    )

    removed = before - len(df)

    print(
        f"\nRemoved missing prices: "
        f"{removed:,} rows"
    )


    before = len(df)

    df = df[
        (df["min_price"] <= df["modal_price"])
        & (
            df["modal_price"]
            <= df["max_price"]
        )
    ].copy()

    removed = before - len(df)

    print(
        f"Removed invalid price ordering: "
        f"{removed:,} rows"
    )

   

    before = len(df)

    df = df[
        df["unit_of_price"]
        .eq("Rs./Quintal")
    ].copy()

    removed = before - len(df)

    print(
        f"Removed non-Rs./Quintal rows: "
        f"{removed:,}"
    )



    commodity_cutoff = (
        df.groupby("commodity_name")[
            "modal_price"
        ]
        .transform(
            lambda s: s.quantile(0.995)
        )
    )

    before = len(df)

    df = df[
        df["modal_price"]
        <= commodity_cutoff
    ].copy()

    removed = before - len(df)

    print(
        f"Removed commodity-level extreme "
        f"price rows: {removed:,}"
    )

   
    series_counts = (
        df.groupby(
            [
                "market_name",
                "commodity_name",
            ]
        )
        .size()
    )

    valid_series = series_counts[
        series_counts >= 365
    ].index

    before = len(df)

    df = (
        df.set_index(
            [
                "market_name",
                "commodity_name",
            ]
        )
        .loc[valid_series]
        .reset_index()
    )

    removed = before - len(df)

    print(
        f"Removed rows from short series: "
        f"{removed:,}"
    )


    sort_columns = [
        "market_name",
        "commodity_name",
        "report_date",
    ]

    df = (
        df.sort_values(sort_columns)
        .reset_index(drop=True)
    )

  

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_pickle(
        output_file
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)

    print(
        f"Final shape: "
        f"{df.shape[0]:,} rows × "
        f"{df.shape[1]} columns"
    )

    print(
        f"Date range: "
        f"{df['report_date'].min().date()} "
        f"to "
        f"{df['report_date'].max().date()}"
    )

    print(
        f"Markets: "
        f"{df['market_name'].nunique():,}"
    )

    print(
        f"Commodities: "
        f"{df['commodity_name'].nunique():,}"
    )

    print(
        f"Market + commodity series: "
        f"{df.groupby(['market_name', 'commodity_name']).ngroups:,}"
    )

    print(
        f"\nSaved processed file:"
    )

    print(output_file)

    print("=" * 70)

    return df



if __name__ == "__main__":

    clean_and_process()
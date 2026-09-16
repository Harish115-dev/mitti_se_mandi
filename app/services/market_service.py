from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "df_reliable.pkl"
)


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed data not found: {DATA_PATH}"
        )

    return pd.read_pickle(DATA_PATH)


def get_markets() -> list[str]:
    df = load_data()

    markets = (
        df["market_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return markets


def get_commodities_for_market(
    market_name: str,
) -> list[str]:

    df = load_data()

    market_query = (
        str(market_name)
        .strip()
        .casefold()
    )

    market_values = (
        df["market_name"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    subset = df[
        market_values == market_query
    ]

    if subset.empty:
        raise ValueError(
            f"No data found for market='{market_name}'"
        )

    commodities = (
        subset["commodity_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return commodities
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
    """
    Load the processed reliable mandi dataset.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed data not found: {DATA_PATH}"
        )

    df = pd.read_pickle(DATA_PATH)

    df["report_date"] = pd.to_datetime(
        df["report_date"],
        errors="coerce",
    )

    return df


def get_recent_data(
    df: pd.DataFrame,
    recent_days: int = 30,
) -> pd.DataFrame:
    """
    Keep only records from the latest available
    dataset date minus recent_days.

    We use the latest date present in the dataset
    rather than the computer's current date.

    Example:
        latest dataset date = 2026-09-16
        recent_days = 30

        cutoff = 2026-08-17
    """

    if recent_days < 0:
        raise ValueError(
            "recent_days must be greater than or equal to 0"
        )

    if df.empty:
        return df.copy()

    latest_date = df["report_date"].max()

    if pd.isna(latest_date):
        raise ValueError(
            "No valid report dates found in processed data."
        )

    cutoff_date = (
        latest_date
        - pd.Timedelta(days=recent_days)
    )

    recent_df = df[
        df["report_date"] >= cutoff_date
    ].copy()

    return recent_df


def get_markets(
    recent_days: int = 30,
) -> list[str]:
    """
    Return markets that have at least one
    record within the recent-data window.
    """

    df = load_data()

    recent_df = get_recent_data(
        df,
        recent_days=recent_days,
    )

    markets = (
        recent_df["market_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return markets


def get_commodities_for_market(
    market_name: str,
    recent_days: int = 30,
) -> list[str]:
    """
    Return only commodities for the selected market
    that have data within the recent-data window.
    """

    df = load_data()

    recent_df = get_recent_data(
        df,
        recent_days=recent_days,
    )

    market_query = (
        str(market_name)
        .strip()
        .casefold()
    )

    market_values = (
        recent_df["market_name"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    subset = recent_df[
        market_values == market_query
    ]

    if subset.empty:
        raise ValueError(
            f"No recent data found for market='{market_name}'"
        )

    commodities = (
        subset["commodity_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return commodities
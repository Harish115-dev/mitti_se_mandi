from __future__ import annotations

import numpy as np
import pandas as pd


GROUP_KEYS = ["market_name", "commodity_name"]

CROSS_FEATURES = [
    "same_day_market_count",
    "cross_market_mean",
    "same_day_price_median_all",
    "price_vs_market_median",
    "price_vs_other_market_mean",
    "pct_other_markets_up",
    "pct_other_markets_down",
]

LOG_SOURCE_COLUMNS = [
    "modal_price",
    "min_price",
    "max_price",
    "price_lag_1",
    "price_lag_2",
    "price_lag_3",
    "price_lag_7",
    "price_roll_mean_7",
    "price_roll_std_7",
    "price_roll_mean_30",
]

LOG_FEATURES = [
    f"log_{col}"
    for col in LOG_SOURCE_COLUMNS
]

REG_FEATURES_7D = [
    "market_name",
    "commodity_name",
    "arrivals",
    "days_since_last_report",
    "year",
    "month",
    "day_of_week",
    "week_of_year",
    *LOG_FEATURES,
    *CROSS_FEATURES,
]


def build_daily_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert cleaned raw mandi data into one row per
    market + commodity + report_date.
    """
    required = [
        "market_name",
        "commodity_name",
        "report_date",
        "modal_price",
        "min_price",
        "max_price",
        "arrivals",
        "variety",
        "grade",
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    daily = (
        df.groupby(
            GROUP_KEYS + ["report_date"],
            as_index=False
        )
        .agg(
            modal_price=("modal_price", "median"),
            min_price=("min_price", "median"),
            max_price=("max_price", "median"),
            arrivals=("arrivals", "sum"),
            variety_count=("variety", "nunique"),
            grade_count=("grade", "nunique"),
        )
    )

    daily["report_date"] = pd.to_datetime(
        daily["report_date"]
    )

    return daily


def add_historical_features(
    df_daily: pd.DataFrame
) -> pd.DataFrame:
    """
    Add lag, rolling, and calendar features.
    """
    df = df_daily.copy()

    df = df.sort_values(
        GROUP_KEYS + ["report_date"]
    ).reset_index(drop=True)

    grp = df.groupby(GROUP_KEYS)["modal_price"]

    # Calendar features
    df["year"] = df["report_date"].dt.year
    df["month"] = df["report_date"].dt.month
    df["day_of_week"] = df["report_date"].dt.dayofweek

    df["week_of_year"] = (
        df["report_date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # Reporting gap
    df["days_since_last_report"] = (
        df.groupby(GROUP_KEYS)["report_date"]
        .diff()
        .dt.days
    )

    # Price lags
    df["price_lag_1"] = grp.shift(1)
    df["price_lag_2"] = grp.shift(2)
    df["price_lag_3"] = grp.shift(3)
    df["price_lag_7"] = grp.shift(7)

    # Historical rolling features
    df["price_roll_mean_7"] = (
        grp.transform(
            lambda s:
            s.shift(1)
            .rolling(7, min_periods=3)
            .mean()
        )
    )

    df["price_roll_std_7"] = (
        grp.transform(
            lambda s:
            s.shift(1)
            .rolling(7, min_periods=3)
            .std()
        )
    )

    df["price_roll_mean_30"] = (
        grp.transform(
            lambda s:
            s.shift(1)
            .rolling(30, min_periods=5)
            .mean()
        )
    )

    return df


def add_cross_market_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Add same-day cross-market features at commodity level.
    """
    df = df.copy()

    commodity_day = (
        df.groupby(
            ["commodity_name", "report_date"]
        )
        .agg(
            same_day_market_count=(
                "market_name",
                "nunique"
            ),
            cross_market_mean=(
                "modal_price",
                "mean"
            ),
            same_day_price_median_all=(
                "modal_price",
                "median"
            ),
        )
        .reset_index()
    )

    df = df.merge(
        commodity_day,
        on=["commodity_name", "report_date"],
        how="left",
    )

    # Mean price of all OTHER markets
    other_market_mean = (
        (
            df["cross_market_mean"]
            * df["same_day_market_count"]
        )
        - df["modal_price"]
    ) / (
        df["same_day_market_count"] - 1
    )

    df["price_vs_market_median"] = (
        df["modal_price"]
        / df["same_day_price_median_all"]
    )

    df["price_vs_other_market_mean"] = (
        df["modal_price"]
        / other_market_mean
    )

    # Current market movement
    market_change = (
        df["modal_price"]
        / df["price_lag_1"]
        - 1
    )

    temp = df.assign(
        market_up=market_change > 0.02,
        market_down=market_change < -0.02,
    )

    movement_stats = (
        temp.groupby(
            ["commodity_name", "report_date"]
        )
        .agg(
            total_markets=("market_name", "count"),
            total_up=("market_up", "sum"),
            total_down=("market_down", "sum"),
        )
        .reset_index()
    )

    df = df.merge(
        movement_stats,
        on=["commodity_name", "report_date"],
        how="left",
    )

    other_count = df["total_markets"] - 1

    df["pct_other_markets_up"] = np.where(
        other_count > 0,
        (
            df["total_up"]
            - (market_change > 0.02).astype(int)
        ) / other_count,
        np.nan,
    )

    df["pct_other_markets_down"] = np.where(
        other_count > 0,
        (
            df["total_down"]
            - (market_change < -0.02).astype(int)
        ) / other_count,
        np.nan,
    )

    df.drop(
        columns=[
            "total_markets",
            "total_up",
            "total_down",
        ],
        inplace=True,
    )

    return df


def add_log_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Add log-transformed price features used by the models.
    """
    df = df.copy()

    for col in LOG_SOURCE_COLUMNS:
        df[f"log_{col}"] = np.log1p(
            df[col].clip(lower=0)
        )

    return df


def build_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Complete production feature pipeline.

    Raw cleaned data
        -> daily aggregation
        -> historical features
        -> cross-market features
        -> log features
    """
    daily = build_daily_data(df)

    daily = add_historical_features(daily)

    daily = add_cross_market_features(daily)

    daily = add_log_features(daily)

    return daily


def get_latest_feature_row(
    df_features: pd.DataFrame,
    market_name: str,
    commodity_name: str,
) -> pd.DataFrame:
    """
    Return the latest available feature row for a
    market + commodity pair.

    Matching is:
    - case-insensitive
    - whitespace-tolerant
    """

    market_query = str(
        market_name
    ).strip().casefold()

    commodity_query = str(
        commodity_name
    ).strip().casefold()

    market_values = (
        df_features["market_name"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    commodity_values = (
        df_features["commodity_name"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    subset = df_features[
        (market_values == market_query)
        & (commodity_values == commodity_query)
    ].copy()

    if subset.empty:
        raise ValueError(
            f"No data found for market='{market_name}', "
            f"commodity='{commodity_name}'"
        )

    subset = subset.sort_values(
        "report_date"
    )

    latest = subset.tail(1).copy()

    # Preserve categorical types expected by LightGBM
    latest["market_name"] = (
        latest["market_name"].astype("category")
    )

    latest["commodity_name"] = (
        latest["commodity_name"].astype("category")
    )

    return latest
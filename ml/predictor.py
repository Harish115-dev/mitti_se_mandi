from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import pandas as pd

from ml.features import (
    REG_FEATURES_7D,
    build_features,
    get_latest_feature_row,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "data" / "models"
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "df_reliable.pkl"




class PricePredictor:
    def __init__(
        self,
        model_dir: Path = MODEL_DIR,
        data_path: Path = DATA_PATH,
    ):
        self.model_dir = Path(model_dir)
        self.data_path = Path(data_path)

        # Load decision configuration
        config_path = (
            self.model_dir / "decision_config_7day.json"
        )

        with open(config_path, "r", encoding="utf-8") as f:
            self.decision_config = json.load(f)

        self.decision_threshold = float(
            self.decision_config["decision_threshold_pct"]
        )

        # Load all 7 trained models
        self.models: dict[int, lgb.Booster] = {}

        for horizon in range(1, 8):
            model_path = (
                self.model_dir
                / f"lightgbm_7day_{horizon}d.txt"
            )

            if not model_path.exists():
                raise FileNotFoundError(
                    f"Model file not found: {model_path}"
                )

            self.models[horizon] = lgb.Booster(
                model_file=str(model_path)
            )

        # Load historical cleaned data
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Data file not found: {self.data_path}"
            )

        self.df_reliable = pd.read_pickle(
            self.data_path
        )

        # Build production features
        self.df_features = build_features(
            self.df_reliable
        )

    def predict(
        self,
        market_name: str,
        commodity_name: str,
    ) -> dict[str, Any]:

        latest = get_latest_feature_row(
            self.df_features,
            market_name=market_name,
            commodity_name=commodity_name,
        )

        # Use only the exact features expected by the models
        X = latest[REG_FEATURES_7D].copy()

        # Make category handling explicit
        X["market_name"] = (
            X["market_name"].astype("category")
        )
        X["commodity_name"] = (
            X["commodity_name"].astype("category")
        )

        forecast: dict[str, float] = {}

        for horizon in range(1, 8):
            model = self.models[horizon]

            pred_log = model.predict(X)

            pred_price = float(
                np.expm1(pred_log[0])
            )

            forecast[f"day_{horizon}"] = pred_price

        current_price = float(
            latest["modal_price"].iloc[0]
        )

        final_price = forecast["day_7"]

        predicted_change_pct = (
            (final_price - current_price)
            / current_price
        ) * 100

        # Final farmer decision
        if predicted_change_pct > self.decision_threshold:
            recommendation = "HOLD"

        elif predicted_change_pct < -self.decision_threshold:
            recommendation = "SELL"

        else:
            recommendation = "NO STRONG SIGNAL"

        return {
            "market": market_name,
            "commodity": commodity_name,
            "report_date": str(
                latest["report_date"].iloc[0].date()
            ),
            "current_price": current_price,
            "forecast": forecast,
            "predicted_change_7d_pct": predicted_change_pct,
            "recommendation": recommendation,
        }


# Simple local test
if __name__ == "__main__":
    predictor = PricePredictor()

    result = predictor.predict(
        market_name="APMC Aatpadi",
        commodity_name="Pomegranate",
    )

    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ))
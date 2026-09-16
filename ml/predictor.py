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

DECISION_CONFIG_PATH = MODEL_DIR / "decision_config_7day.json"




class PricePredictor:

    def __init__(
        self,
        model_dir: Path = MODEL_DIR,
        data_path: Path = DATA_PATH,
    ) -> None:

        self.model_dir = Path(model_dir)
        self.data_path = Path(data_path)


        if not DECISION_CONFIG_PATH.exists():
            raise FileNotFoundError(
                f"Decision config not found: {DECISION_CONFIG_PATH}"
            )

        with open(
            DECISION_CONFIG_PATH,
            "r",
            encoding="utf-8",
        ) as f:
            config = json.load(f)

        self.decision_threshold = float(
            config["decision_threshold_pct"]
        )

        # Load seven LightGBM models
      

        self.models: dict[int, lgb.Booster] = {}

        for horizon in range(1, 8):

            model_path = (
                self.model_dir
                / f"lightgbm_7day_{horizon}d.txt"
            )

            if not model_path.exists():
                raise FileNotFoundError(
                    f"Model not found: {model_path}"
                )

            self.models[horizon] = lgb.Booster(
                model_file=str(model_path)
            )

       
        # Load processed reliable dataset
   

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Processed data not found: {self.data_path}"
            )

        self.df_reliable = pd.read_pickle(
            self.data_path
        )

    

        self.df_features = build_features(
            self.df_reliable
        )


    
    # predict
    

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

        X = latest[REG_FEATURES_7D].copy()

        X["market_name"] = (
            X["market_name"].astype("category")
        )

        X["commodity_name"] = (
            X["commodity_name"].astype("category")
        )

        report_date = pd.Timestamp(
            latest["report_date"].iloc[0]
        )

        #7-day forecast
    

        forecast: dict[str, dict[str, Any]] = {}

        for horizon in range(1, 8):

            model = self.models[horizon]

            # Model predicts log1p(price)
            pred_log = model.predict(X)

            # Convert back to original price
            pred_price = float(
                np.expm1(pred_log[0])
            )

            # Actual future calendar date
            forecast_date = (
                report_date
                + pd.Timedelta(days=horizon)
            )

            forecast[f"day_{horizon}"] = {
                "date": forecast_date.strftime(
                    "%Y-%m-%d"
                ),
                "price": round(
                    pred_price,
                    2,
                ),
            }


        current_price = float(
            latest["modal_price"].iloc[0]
        )



        final_price = forecast["day_7"]["price"]


        if current_price == 0:

            predicted_change_pct = 0.0

        else:

            predicted_change_pct = (
                (
                    final_price
                    - current_price
                )
                / current_price
            ) * 100

    
        # Decision logic
        # > +10%  -> HOLD
        # < -10%  -> SELL
        # otherwise -> NO STRONG SIGNAL
        

        if (
            predicted_change_pct
            > self.decision_threshold
        ):

            recommendation = "HOLD"

        elif (
            predicted_change_pct
            < -self.decision_threshold
        ):

            recommendation = "SELL"

        else:

            recommendation = "NO STRONG SIGNAL"


        # Final response


        return {
            "market": str(
                latest["market_name"].iloc[0]
            ),

            "commodity": str(
                latest["commodity_name"].iloc[0]
            ),

            "report_date": report_date.strftime(
                "%Y-%m-%d"
            ),

            "current_price": round(
                current_price,
                2,
            ),

            "forecast": forecast,

            "predicted_change_7d_pct": round(
                predicted_change_pct,
                2,
            ),

            "recommendation": recommendation,
        }



# LOCAL TEST


if __name__ == "__main__":

    predictor = PricePredictor()

    result = predictor.predict(
        market_name="APMC Aatpadi",
        commodity_name="Pomegranate",
    )

    print("\n" + "=" * 60)
    print("7-DAY PRICE FORECAST")
    print("=" * 60)

    print(
        f"Market      : {result['market']}"
    )

    print(
        f"Commodity   : {result['commodity']}"
    )

    print(
        f"Report Date : {result['report_date']}"
    )

    print(
        f"Current Price : ₹{result['current_price']:.2f}"
    )

    print("\nForecast:")

    for day, values in result["forecast"].items():

        print(
            f"{day}: "
            f"{values['date']} -> "
            f"₹{values['price']:.2f}"
        )

    print(
        "\nPredicted 7-Day Change : "
        f"{result['predicted_change_7d_pct']:.2f}%"
    )

    print(
        "Recommendation          : "
        f"{result['recommendation']}"
    )

    print("=" * 60)
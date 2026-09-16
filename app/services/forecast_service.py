from ml.predictor import PricePredictor


# Create one predictor instance when the application starts.
predictor = PricePredictor()


def get_forecast(
    market_name: str,
    commodity_name: str,
):
    return predictor.predict(
        market_name=market_name,
        commodity_name=commodity_name,
    )
from flask import Blueprint, jsonify, request

from app.services.forecast_service import get_forecast


forecast_bp = Blueprint(
    "forecast",
    __name__,
    url_prefix="/api/forecast",
)


@forecast_bp.get("/")
def forecast():

    market_name = request.args.get("market")
    commodity_name = request.args.get("commodity")

    if not market_name or not commodity_name:
        return jsonify(
            {
                "error": "market and commodity are required"
            }
        ), 400

    try:
        result = get_forecast(
            market_name=market_name,
            commodity_name=commodity_name,
        )

        return jsonify(result), 200

    except ValueError as exc:
        return jsonify(
            {
                "error": str(exc)
            }
        ), 404

    except Exception as exc:
        return jsonify(
            {
                "error": "Failed to generate forecast",
                "details": str(exc),
            }
        ), 500
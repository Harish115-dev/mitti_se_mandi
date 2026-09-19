from flask import Blueprint, jsonify

from app.services.market_service import (
    get_markets,
    get_commodities_for_market,
)


market_bp = Blueprint(
    "markets",
    __name__,
    url_prefix="/api/markets",
)


# Only expose market/commodity combinations with
# data available within the latest 30 days.
RECENT_DAYS = 30


@market_bp.get("/")
def markets():

    try:

        result = get_markets(
            recent_days=RECENT_DAYS
        )

        return jsonify(
            {
                "markets": result
            }
        ), 200

    except Exception as exc:

        return jsonify(
            {
                "error": "Failed to load markets",
                "details": str(exc),
            }
        ), 500


@market_bp.get("/<path:market_name>/commodities")
def commodities(market_name):

    try:

        result = get_commodities_for_market(
            market_name=market_name,
            recent_days=RECENT_DAYS,
        )

        return jsonify(
            {
                "market": market_name,
                "commodities": result,
            }
        ), 200

    except ValueError as exc:

        return jsonify(
            {
                "error": str(exc)
            }
        ), 404

    except Exception as exc:

        return jsonify(
            {
                "error": "Failed to load commodities",
                "details": str(exc),
            }
        ), 500
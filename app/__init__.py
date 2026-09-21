import os

from datetime import timedelta

from flask import Flask


def create_app():

    app = Flask(__name__)

 
    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "mitti-se-mandi-dev-secret-key"
    )

  
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # IMPORTANT for local HTTP development
    app.config["SESSION_COOKIE_SECURE"] = False

    app.config["SESSION_REFRESH_EACH_REQUEST"] = True

 

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.forecast import forecast_bp
    from app.routes.markets import market_bp
    from app.routes.lots import lots_bp
    from app.routes.offers import offers_bp
    from app.routes.crops import crops_bp
    from app.routes.transactions import transactions_bp
    from app.routes.buyer_requirements import buyer_requirements_bp
    from app.routes.payments import payments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(forecast_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(lots_bp)
    app.register_blueprint(offers_bp)
    app.register_blueprint(crops_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(buyer_requirements_bp)
    app.register_blueprint(payments_bp)

    @app.route("/")
    @app.route("/index")
    def home():
        from flask import render_template
        return render_template("index.html")

    return app
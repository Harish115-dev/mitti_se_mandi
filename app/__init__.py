from flask import Flask, render_template
import os
from datetime import timedelta
from flask import Flask
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY",
    "dev-key-change-me"
)

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_REFRESH_EACH_REQUEST"] = True


from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.forecast import forecast_bp
from app.routes.markets import market_bp
from app.routes.lots import lots_bp
from app.routes.offers import offers_bp
from app.routes.crops import crops_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(forecast_bp)
app.register_blueprint(market_bp)
app.register_blueprint(lots_bp)
app.register_blueprint(offers_bp)
app.register_blueprint(crops_bp)


@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")
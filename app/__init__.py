from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "dev-key-change-me"

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
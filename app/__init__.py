from flask import Flask, render_template

from app.config import Config


app = Flask(__name__)
app.config.from_object(Config)

from app.routes.auth import auth_bp
from app.routes.forecast import forecast_bp
from app.routes.markets import market_bp
from app.routes.dashboard import dashboard_bp
from app.routes.crops import crops_bp

app.register_blueprint(auth_bp)
app.register_blueprint(forecast_bp)
app.register_blueprint(market_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(crops_bp)


@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")

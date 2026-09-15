from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "dev-key-change-me"

from app.routes.auth import auth_bp
from app.routes.forecast import forecast_bp

app.register_blueprint(auth_bp)
app.register_blueprint(forecast_bp)


@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")
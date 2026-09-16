from flask import Blueprint, render_template, session, redirect


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
)


@dashboard_bp.route("/farmer")
def farmer_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "farmer":
        return redirect("/login")

    return render_template(
        "farmer_dashboard.html",
        user_name=session.get("user_name"),
    )


@dashboard_bp.route("/buyer")
def buyer_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "buyer":
        return redirect("/login")

    return render_template(
        "buyer_dashboard.html",
        user_name=session.get("user_name"),
    )
from __future__ import annotations

from functools import wraps
from flask import Blueprint, redirect, render_template, session, url_for

from app.db.database import get_connection


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
)


def farmer_required(view):
    """Require an authenticated farmer for dashboard pages."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("user_role") != "farmer":
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped


@dashboard_bp.route("/farmer")
@farmer_required
def farmer_dashboard():
    """Render the farmer dashboard with real DB-backed farmer data."""

    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                full_name,
                email,
                phone,
                state,
                city,
                address,
                crops,
                land_size,
                created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )

        farmer = cursor.fetchone()

        if not farmer:
            session.clear()
            return redirect(url_for("auth.login"))

        cursor.execute(
            """
            SELECT
                id,
                crop_name,
                quantity,
                grade,
                price,
                status,
                created_at
            FROM crops
            WHERE farmer_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )

        crops = cursor.fetchall()

        for crop in crops:
            if crop.get("created_at") is not None:
                crop["created_at"] = crop["created_at"].strftime(
                    "%Y-%m-%d"
                )

        if farmer.get("created_at") is not None:
            farmer["created_at"] = farmer["created_at"].strftime(
                "%Y-%m-%d"
            )

        return render_template(
            "farmer_dashboard.html",
            farmer=farmer,
            crops=crops,
        )

    finally:
        cursor.close()
        conn.close()


@dashboard_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

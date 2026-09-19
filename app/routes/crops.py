from __future__ import annotations

from functools import wraps

from flask import Blueprint, redirect, request, session, url_for

from app.db.database import get_connection


crops_bp = Blueprint(
    "crops",
    __name__,
    url_prefix="/dashboard/crops",
)


def farmer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("user_role") != "farmer":
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped


@crops_bp.post("/add")
@farmer_required
def add_crop():
    crop_name = request.form.get("crop_name", "").strip()
    quantity_raw = request.form.get("quantity", "").strip()
    grade = request.form.get("grade", "Grade A").strip()
    price_raw = request.form.get("price", "").strip()
    status = request.form.get("status", "Available").strip()

    try:
        quantity = int(quantity_raw)
        price = float(price_raw)
    except ValueError:
        return redirect(
            url_for("dashboard.farmer_dashboard")
        )

    if not crop_name or quantity <= 0 or price <= 0:
        return redirect(
            url_for("dashboard.farmer_dashboard")
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO crops
                (farmer_id, crop_name, quantity, grade, price, status)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            (
                session["user_id"],
                crop_name,
                quantity,
                grade,
                price,
                status,
            ),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("dashboard.farmer_dashboard"))

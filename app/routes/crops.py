from functools import wraps

from flask import Blueprint, request, redirect, url_for, session

from app.db.database import get_connection


crops_bp = Blueprint("crops", __name__, url_prefix="/crops")


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
    grade = request.form.get("grade", "").strip()
    price_raw = request.form.get("price", "").strip()
    status = request.form.get("status", "available").strip().lower()

    # Basic validation
    if not crop_name:
        return "Crop name is required", 400

    if not quantity_raw:
        return "Quantity is required", 400

    if not price_raw:
        return "Expected price is required", 400

    try:
        quantity = float(quantity_raw)
        expected_price = float(price_raw)
    except ValueError:
        return "Quantity and price must be valid numbers", 400

    if quantity <= 0:
        return "Quantity must be greater than 0", 400

    if expected_price <= 0:
        return "Expected price must be greater than 0", 400

    allowed_statuses = {"available", "pending", "sold"}

    if status not in allowed_statuses:
        status = "available"

    farmer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO crops
                (farmer_id, crop_name, quantity, grade, expected_price, status)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            (
                farmer_id,
                crop_name,
                quantity,
                grade,
                expected_price,
                status,
            ),
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("dashboard.farmer_dashboard"))
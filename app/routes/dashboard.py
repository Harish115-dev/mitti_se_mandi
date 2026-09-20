from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from app.services.matching_service import get_buyer_matches

from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)

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
            return redirect(
                url_for("auth.login")
            )

        if session.get("user_role") != "farmer":
            return redirect(
                url_for("auth.login")
            )

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

            return redirect(
                url_for("auth.login")
            )


        cursor.execute(
            """
            SELECT
                id,
                crop_name,
                quantity,
                grade,
                expected_price AS price,
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

                crop["created_at"] = (
                    crop["created_at"]
                    .strftime("%Y-%m-%d")
                )

        if farmer.get("created_at") is not None:

            farmer["created_at"] = (
                farmer["created_at"]
                .strftime("%Y-%m-%d")
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
    """Log the current user out."""

    session.clear()

    return redirect(
        url_for("home")
    )




# ---------- Buyer protection ----------
def buyer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("user_role") != "buyer":
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped


# ---------- Buyer Dashboard ----------
@dashboard_bp.route("/buyer")
@buyer_required
def buyer_dashboard():
    buyer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Buyer profile
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
                business_name,
                interests,
                is_verified,
                created_at
            FROM users
            WHERE id = %s
            """,
            (buyer_id,),
        )

        buyer = cursor.fetchone()

        if not buyer:
            session.clear()
            return redirect(url_for("auth.login"))

        # Buyer requirements
        cursor.execute(
            """
            SELECT
                id,
                crop_name,
                variety,
                min_quantity,
                max_quantity,
                quantity_unit,
                required_grade,
                preferred_location,
                max_price,
                status,
                created_at
            FROM buyer_requirements
            WHERE buyer_id = %s
            ORDER BY created_at DESC
            """,
            (buyer_id,),
        )

        requirements = cursor.fetchall()
        matches = get_buyer_matches(buyer_id)

        active_requirements = sum(
            1 for requirement in requirements
            if requirement["status"] == "active"
        )

        closed_requirements = sum(
            1 for requirement in requirements
            if requirement["status"] == "closed"
        )

        for requirement in requirements:
            if requirement.get("created_at"):
                requirement["created_at"] = (
                    requirement["created_at"].strftime("%Y-%m-%d")
                )

        if buyer.get("created_at"):
            buyer["created_at"] = buyer["created_at"].strftime("%Y-%m-%d")

        return render_template(
        "buyer_dashboard.html",
        buyer=buyer,
        requirements=requirements,
        active_requirements=active_requirements,
        closed_requirements=closed_requirements,
        matches=matches,
        )

    finally:
        cursor.close()
        conn.close()


# ---------- Add Buyer Requirement ----------
@dashboard_bp.route("/buyer/requirements/add", methods=["POST"])
@buyer_required
def add_buyer_requirement():
    buyer_id = session["user_id"]

    crop_name = request.form.get("crop_name", "").strip()
    variety = request.form.get("variety", "").strip()
    min_quantity_raw = request.form.get("min_quantity", "").strip()
    max_quantity_raw = request.form.get("max_quantity", "").strip()
    quantity_unit = request.form.get("quantity_unit", "quintal").strip()
    required_grade = request.form.get("required_grade", "").strip()
    preferred_location = request.form.get("preferred_location", "").strip()
    max_price_raw = request.form.get("max_price", "").strip()

    # Required field
    if not crop_name:
        return "Crop name is required.", 400

    # Convert optional quantities
    min_quantity = None
    max_quantity = None
    max_price = None

    if min_quantity_raw:
        try:
            min_quantity = float(min_quantity_raw)
        except ValueError:
            return "Minimum quantity must be a valid number.", 400

    if max_quantity_raw:
        try:
            max_quantity = float(max_quantity_raw)
        except ValueError:
            return "Maximum quantity must be a valid number.", 400

    if max_price_raw:
        try:
            max_price = float(max_price_raw)
        except ValueError:
            return "Maximum price must be a valid number.", 400

    if min_quantity is not None and min_quantity < 0:
        return "Minimum quantity cannot be negative.", 400

    if max_quantity is not None and max_quantity < 0:
        return "Maximum quantity cannot be negative.", 400

    if (
        min_quantity is not None
        and max_quantity is not None
        and max_quantity < min_quantity
    ):
        return "Maximum quantity cannot be less than minimum quantity.", 400

    if max_price is not None and max_price < 0:
        return "Maximum price cannot be negative.", 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO buyer_requirements
            (
                buyer_id,
                crop_name,
                variety,
                min_quantity,
                max_quantity,
                quantity_unit,
                required_grade,
                preferred_location,
                max_price,
                status
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, 'active'
            )
            """,
            (
                buyer_id,
                crop_name,
                variety or None,
                min_quantity,
                max_quantity,
                quantity_unit or "quintal",
                required_grade or None,
                preferred_location or None,
                max_price,
            ),
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("dashboard.buyer_dashboard"))
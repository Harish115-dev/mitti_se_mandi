import bcrypt

from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    url_for,
)

from app.db.database import get_connection


auth_bp = Blueprint("auth", __name__)


# =========================================================
# LOGIN
# =========================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return "Please enter email and password.", 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, full_name, role, password
            FROM users
            WHERE email = %s
            """,
            (email,),
        )

        user = cursor.fetchone()

        if not user:
            return "No account found with this email.", 404

        stored_password = user["password"]

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password.encode("utf-8"),
        ):
            return "Invalid password. Please try again.", 401

        # -------------------------------------------------
        # Clear any old session first
        # -------------------------------------------------
        session.clear()

        # -------------------------------------------------
        # Create new persistent session
        # -------------------------------------------------
        session.permanent = True

        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_role"] = user["role"]

        # -------------------------------------------------
        # Redirect according to role
        # -------------------------------------------------
        if user["role"] == "farmer":
            return redirect("/dashboard/farmer")

        if user["role"] == "buyer":
            return redirect("/dashboard/buyer")

        # Invalid role
        session.clear()
        return "Invalid user role.", 400

    finally:
        cursor.close()
        conn.close()


# =========================================================
# LOGOUT
# =========================================================
@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():

    # Completely remove all session data
    session.clear()

    # Go back to login page
    return redirect(url_for("auth.login"))


# =========================================================
# REGISTRATION
# =========================================================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("registration.html")

    # -----------------------------------------------------
    # Form data
    # -----------------------------------------------------
    role = request.form.get("role", "").strip().lower()

    full_name = request.form.get("fullName", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    state = request.form.get("state", "").strip()
    city = request.form.get("city", "").strip()
    address = request.form.get("address", "").strip()

    password = request.form.get("password", "")
    confirm_password = request.form.get("confirmPassword", "")

    # Role-specific fields
    crops = request.form.get("crops", "").strip()
    land_size_raw = request.form.get("landSize", "").strip()

    business_name = request.form.get("businessName", "").strip()
    interests = request.form.get("interests", "").strip()

    # -----------------------------------------------------
    # Basic validation
    # -----------------------------------------------------
    if not role or not full_name or not email or not password:
        return "Please fill all required fields.", 400

    if role not in {"farmer", "buyer"}:
        return "Invalid role selected.", 400

    if password != confirm_password:
        return "Passwords do not match.", 400

    # -----------------------------------------------------
    # Convert land size
    # -----------------------------------------------------
    if land_size_raw:
        try:
            land_size = float(land_size_raw)

            if land_size < 0:
                return "Land size cannot be negative.", 400

        except ValueError:
            return "Land size must be a valid number.", 400

    else:
        land_size = None

    # -----------------------------------------------------
    # Database connection
    # -----------------------------------------------------
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Check duplicate email
        # -------------------------------------------------
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,),
        )

        existing = cursor.fetchone()

        if existing:
            return "This email is already registered. Please login.", 409

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        # -------------------------------------------------
        # Insert user
        # -------------------------------------------------
        cursor.execute(
            """
            INSERT INTO users
            (
                role,
                full_name,
                email,
                phone,
                password,
                state,
                city,
                address,
                crops,
                land_size,
                business_name,
                interests
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                role,
                full_name,
                email,
                phone or None,
                hashed_password,
                state or None,
                city or None,
                address or None,
                crops or None,
                land_size,
                business_name or None,
                interests or None,
            ),
        )

        conn.commit()

        # -------------------------------------------------
        # Start session after registration
        # -------------------------------------------------
        session.clear()

        session.permanent = True

        session["user_id"] = cursor.lastrowid
        session["user_name"] = full_name
        session["user_role"] = role

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

    # -----------------------------------------------------
    # Redirect according to role
    # -----------------------------------------------------
    if role == "farmer":
        return redirect("/dashboard/farmer")

    return redirect("/dashboard/buyer")
import bcrypt
from flask import Blueprint, request, session, redirect, render_template

from app.db.database import get_connection

auth_bp = Blueprint("auth", __name__)


# ---------- ported from login/login.php ----------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "")
    password = request.form.get("password", "")

    if not email or not password:
        return "Please enter email and password.", 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. User ko email se find karein
    cursor.execute(
        "SELECT id, full_name, role, password FROM users WHERE email = %s",
        (email,),
    )
    rows = cursor.fetchall()

    if len(rows) == 1:
        user = rows[0]

        # 2. Password verify karein
        if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):

            # 3. Session set karein
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_role"] = user["role"]

            cursor.close()
            conn.close()

            # 4. Role ke according redirect
            if user["role"] == "farmer":
                return redirect("/dashboard/farmer")
            else:
                return redirect("/dashboard/buyer")
        else:
            cursor.close()
            conn.close()
            return "Invalid password. Please try again.", 401
    else:
        cursor.close()
        conn.close()
        return "No account found with this email.", 404


# ---------- ported from registration/register.php ----------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("registration.html")

    # 1. Form data receive karein
    role = request.form.get("role", "")
    fullName = request.form.get("fullName", "")
    email = request.form.get("email", "")
    phone = request.form.get("phone", "")
    state = request.form.get("state", "")
    city = request.form.get("city", "")
    address = request.form.get("address", "")
    password = request.form.get("password", "")
    confirmPassword = request.form.get("confirmPassword", "")

    # Role-specific fields
    crops = request.form.get("crops", "")
    landSize = request.form.get("landSize", "")
    businessName = request.form.get("businessName", "")
    interests = request.form.get("interests", "")

    # 2. Basic validation
    if not role or not fullName or not email or not password:
        return "Please fill all required fields.", 400

    if password != confirmPassword:
        return "Passwords do not match.", 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 3. Email already exists check karein
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    existing = cursor.fetchall()

    if len(existing) > 0:
        cursor.close()
        conn.close()
        return "This email is already registered. Please login.", 409

    # 4. Password hash karein (SECURITY!)
    hashedPassword = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # 5. Data insert karein
    cursor.execute(
        """
        INSERT INTO users
        (role, full_name, email, phone, password, state, city, address, crops, land_size, business_name, interests)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (role, fullName, email, phone, hashedPassword,
         state, city, address, crops, landSize, businessName, interests),
    )
    conn.commit()

    # Registration successful
    session["user_id"] = cursor.lastrowid
    session["user_name"] = fullName
    session["user_role"] = role

    cursor.close()
    conn.close()

    # Redirect based on role
    if role == "farmer":
        return redirect("/dashboard/farmer")
    else:
        return redirect("/dashboard/buyer")

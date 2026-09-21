from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)

from app.db.database import get_connection


buyer_requirements_bp = Blueprint(
    "buyer_requirements",
    __name__,
    url_prefix="/buyer-requirements",
)


# =========================================================
# FARMER AUTH
# =========================================================

def farmer_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("user_role") != "farmer":
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped


# =========================================================
# FARMER - FIND BUYERS
# =========================================================

@buyer_requirements_bp.route("/farmer")
@farmer_required
def farmer_buyer_requirements():

    farmer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Get farmer information
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                id,
                full_name,
                city,
                state
            FROM users
            WHERE id = %s
            """,
            (farmer_id,),
        )

        farmer = cursor.fetchone()

        if not farmer:
            return "Farmer not found.", 404


        # -------------------------------------------------
        # Get farmer crops
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                id,
                crop_name,
                quantity,
                quantity_unit,
                grade,
                expected_price,
                market_name,
                status
            FROM crops
            WHERE farmer_id = %s
              AND status IN ('available', 'listed')
            ORDER BY created_at DESC
            """,
            (farmer_id,),
        )

        farmer_crops = cursor.fetchall()


        # -------------------------------------------------
        # Get active buyer requirements
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                br.id,
                br.buyer_id,
                br.crop_name,
                br.variety,
                br.min_quantity,
                br.max_quantity,
                br.quantity_unit,
                br.required_grade,
                br.preferred_location,
                br.max_price,
                br.status,
                br.created_at,

                u.full_name AS buyer_name,
                u.city AS buyer_city,
                u.state AS buyer_state,
                u.business_name

            FROM buyer_requirements br

            JOIN users u
                ON u.id = br.buyer_id

            WHERE br.status = 'active'

            ORDER BY br.created_at DESC
            """
        )

        requirements = cursor.fetchall()


        # -------------------------------------------------
        # Build farmer-side matching information
        # -------------------------------------------------
        result = []


        for requirement in requirements:

            requirement_crop = (
    str(
        requirement["crop_name"] or ""
    )
    .strip()
    .lower()
)

            # Find farmer crop with same crop name
            matched_crop = None

            for crop in farmer_crops:

                farmer_crop_name = (
                    str(
                        crop["crop_name"] or ""
                    )
                    .strip()
                    .lower()
                )

                if farmer_crop_name == requirement_crop:

                    matched_crop = crop

                    break


            # ---------------------------------------------
            # If farmer does not grow this crop
            # ---------------------------------------------
            if not matched_crop:

                requirement["match_percentage"] = 0

                requirement["match_status"] = (
                    "Different Crop"
                )

                requirement["checks"] = [
                    {
                        "name": "Crop",
                        "passed": False,
                    }
                ]

                requirement["matched_crop"] = None

                result.append(requirement)

                continue


            checks = []


            # ---------------------------------------------
            # Quantity check
            # ---------------------------------------------
            farmer_quantity = float(
                matched_crop["quantity"] or 0
            )

            min_quantity = (
                float(requirement["min_quantity"])
                if requirement["min_quantity"] is not None
                else None
            )

            max_quantity = (
                float(requirement["max_quantity"])
                if requirement["max_quantity"] is not None
                else None
            )


            quantity_pass = True


            if min_quantity is not None:
                quantity_pass = (
                    farmer_quantity >= min_quantity
                )


            if (
                max_quantity is not None
                and farmer_quantity > max_quantity
            ):
                quantity_pass = False


            checks.append(
                {
                    "name": "Quantity",
                    "passed": quantity_pass,
                }
            )


            # ---------------------------------------------
            # Grade check
            # ---------------------------------------------
            farmer_grade = (
                str(
                    matched_crop["grade"] or ""
                )
                .lower()
                .replace("grade", "")
                .strip()
            )


            required_grade = (
                str(
                    requirement["required_grade"] or ""
                )
                .lower()
                .replace("grade", "")
                .strip()
            )


            grade_pass = (
                not required_grade
                or farmer_grade == required_grade
            )


            checks.append(
                {
                    "name": "Grade",
                    "passed": grade_pass,
                }
            )


            # ---------------------------------------------
            # Location check
            # ---------------------------------------------
            preferred_location = (
                str(
                    requirement[
                        "preferred_location"
                    ] or ""
                )
                .strip()
                .lower()
            )


            farmer_market = (
                str(
                    matched_crop["market_name"] or ""
                )
                .strip()
                .lower()
            )


            farmer_city = (
                str(
                    farmer["city"] or ""
                )
                .strip()
                .lower()
            )


            farmer_state = (
                str(
                    farmer["state"] or ""
                )
                .strip()
                .lower()
            )


            location_pass = (
                not preferred_location
                or preferred_location in farmer_market
                or preferred_location in farmer_city
                or preferred_location in farmer_state
            )


            checks.append(
                {
                    "name": "Location",
                    "passed": location_pass,
                }
            )


            # ---------------------------------------------
            # Price check
            # ---------------------------------------------
            farmer_price = float(
                matched_crop["expected_price"] or 0
            )


            max_price = (
                float(requirement["max_price"])
                if requirement["max_price"] is not None
                else None
            )


            price_pass = (
                max_price is None
                or farmer_price <= max_price
            )


            checks.append(
                {
                    "name": "Price",
                    "passed": price_pass,
                }
            )


            # ---------------------------------------------
            # Match percentage
            # ---------------------------------------------
            passed_count = sum(
                1
                for check in checks
                if check["passed"]
            )


            match_percentage = int(
                (passed_count / len(checks)) * 100
            )


            if match_percentage == 100:

                match_status = "Full Match"

            elif match_percentage > 0:

                match_status = "Partial Match"

            else:

                match_status = "Low Match"


            # ---------------------------------------------
            # Add match information
            # ---------------------------------------------
            requirement["match_percentage"] = (
                match_percentage
            )

            requirement["match_status"] = (
                match_status
            )

            requirement["checks"] = checks

            requirement["matched_crop"] = (
                matched_crop
            )


            result.append(requirement)


        return render_template(
            "farmer_buyer_requirements.html",
            farmer=farmer,
            requirements=result,
        )


    finally:

        cursor.close()
        conn.close()
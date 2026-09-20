from functools import wraps

from flask import Blueprint, redirect, session, url_for

from app.db.database import get_connection


lots_bp = Blueprint(
    "lots",
    __name__,
    url_prefix="/lots",
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


@lots_bp.post("/publish/<int:crop_id>")
@farmer_required
def publish_crop(crop_id):

    farmer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # 1. Get the farmer's crop
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                crop_name,
                variety,
                quantity,
                quantity_unit,
                grade,
                expected_price,
                market_name,
                status
            FROM crops
            WHERE id = %s
              AND farmer_id = %s
            """,
            (crop_id, farmer_id),
        )

        crop = cursor.fetchone()

        if not crop:
            return "Crop not found.", 404


        # -------------------------------------------------
        # 2. Only available crops can be published
        # -------------------------------------------------

        if crop["status"] != "available":
            return (
                "Only available crops can be published.",
                400,
            )


        # -------------------------------------------------
        # 3. Get farmer location
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                city,
                state,
                address
            FROM users
            WHERE id = %s
            """,
            (farmer_id,),
        )

        farmer = cursor.fetchone() or {}


        location_parts = [
            farmer.get("city"),
            farmer.get("state"),
        ]

        location = ", ".join(
            part.strip()
            for part in location_parts
            if part and part.strip()
        )


        # -------------------------------------------------
        # 4. Generate unique lot code
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM lots
            WHERE farmer_id = %s
            """,
            (farmer_id,),
        )

        result = cursor.fetchone()

        lot_number = int(result["total"] or 0) + 1

        lot_code = (
            f"LOT-{farmer_id}-{lot_number:04d}"
        )


        # -------------------------------------------------
        # 5. Create LOT
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO lots
            (
                farmer_id,
                lot_code,
                crop_name,
                variety,
                quantity,
                quantity_unit,
                grade,
                expected_price,
                market_name,
                location,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'published'
            )
            """,
            (
                farmer_id,
                lot_code,
                crop["crop_name"],
                crop["variety"],
                crop["quantity"],
                crop["quantity_unit"] or "quintal",
                crop["grade"],
                crop["expected_price"],
                crop["market_name"],
                location or None,
            ),
        )

        lot_id = cursor.lastrowid


        # -------------------------------------------------
        # 6. Create LISTING
        # -------------------------------------------------

        title = (
            f"{crop['crop_name']} - "
            f"{crop['quantity']} "
            f"{crop['quantity_unit'] or 'quintal'}"
        )


        description_parts = []

        if crop["variety"]:
            description_parts.append(
                f"Variety: {crop['variety']}"
            )

        if crop["grade"]:
            description_parts.append(
                f"Grade: {crop['grade']}"
            )

        if location:
            description_parts.append(
                f"Location: {location}"
            )

        description = " | ".join(
            description_parts
        ) or None


        cursor.execute(
            """
            INSERT INTO listings
            (
                lot_id,
                farmer_id,
                title,
                description,
                asking_price,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                'active'
            )
            """,
            (
                lot_id,
                farmer_id,
                title,
                description,
                crop["expected_price"],
            ),
        )


        # -------------------------------------------------
        # 7. Mark original crop as LISTED
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE crops
            SET status = 'listed'
            WHERE id = %s
              AND farmer_id = %s
            """,
            (
                crop_id,
                farmer_id,
            ),
        )


        # -------------------------------------------------
        # 8. Commit everything together
        # -------------------------------------------------

        conn.commit()


    except Exception:

        conn.rollback()
        raise


    finally:

        cursor.close()
        conn.close()


    return redirect(
        url_for(
            "dashboard.farmer_dashboard"
        )
    )
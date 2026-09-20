from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.db.database import get_connection


offers_bp = Blueprint(
    "offers",
    __name__,
    url_prefix="/offers",
)


# =========================================================
# AUTH HELPERS
# =========================================================

def buyer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("user_role") != "buyer":
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped


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
# BUYER - CREATE OFFER
# =========================================================

@offers_bp.route(
    "/create/<int:listing_id>",
    methods=["GET", "POST"],
)
@buyer_required
def create_offer(listing_id):

    buyer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                l.id AS listing_id,
                l.farmer_id,
                l.title,
                l.description,
                l.asking_price,
                l.status,

                lot.crop_name,
                lot.quantity,
                lot.quantity_unit,
                lot.grade,
                lot.location,

                u.full_name AS farmer_name

            FROM listings l

            JOIN lots lot
                ON lot.id = l.lot_id

            JOIN users u
                ON u.id = l.farmer_id

            WHERE l.id = %s
              AND l.status = 'active'
            """,
            (listing_id,),
        )

        listing = cursor.fetchone()

        if not listing:
            return (
                "Listing not found or no longer active.",
                404,
            )

        if listing["farmer_id"] == buyer_id:
            return (
                "You cannot make an offer on your own listing.",
                403,
            )

        # GET = display form
        if request.method == "GET":

            return render_template(
                "make_offer.html",
                listing=listing,
            )

        # POST = create offer
        quantity_raw = request.form.get(
            "quantity",
            "",
        ).strip()

        offered_price_raw = request.form.get(
            "offered_price",
            "",
        ).strip()

        message = request.form.get(
            "message",
            "",
        ).strip()

        try:
            quantity = float(quantity_raw)
        except ValueError:
            return "Quantity must be a valid number.", 400

        try:
            offered_price = float(
                offered_price_raw
            )
        except ValueError:
            return (
                "Offered price must be a valid number.",
                400,
            )

        if quantity <= 0:
            return (
                "Quantity must be greater than 0.",
                400,
            )

        if offered_price <= 0:
            return (
                "Offered price must be greater than 0.",
                400,
            )

        listing_quantity = float(
            listing["quantity"]
        )

        if quantity > listing_quantity:
            return (
                f"Offer quantity cannot exceed "
                f"{listing_quantity} "
                f"{listing['quantity_unit']}.",
                400,
            )

        # Prevent duplicate pending offer
        cursor.execute(
            """
            SELECT id
            FROM offers
            WHERE listing_id = %s
              AND buyer_id = %s
              AND status = 'pending'
            LIMIT 1
            """,
            (
                listing_id,
                buyer_id,
            ),
        )

        existing_offer = cursor.fetchone()

        if existing_offer:
            return (
                "You already have a pending offer "
                "for this listing.",
                409,
            )

        cursor.execute(
            """
            INSERT INTO offers
            (
                listing_id,
                buyer_id,
                quantity,
                offered_price,
                message,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                'pending'
            )
            """,
            (
                listing_id,
                buyer_id,
                quantity,
                offered_price,
                message or None,
            ),
        )

        conn.commit()

        return redirect(
            url_for(
                "dashboard.buyer_dashboard"
            )
        )

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


# =========================================================
# FARMER - OFFER INBOX
# =========================================================

@offers_bp.route("/farmer")
@farmer_required
def farmer_offers():

    farmer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                o.id AS offer_id,
                o.listing_id,
                o.quantity AS offer_quantity,
                o.offered_price,
                o.message,
                o.status,
                o.created_at,

                l.title AS listing_title,
                l.asking_price,

                lot.crop_name,
                lot.quantity AS listing_quantity,
                lot.quantity_unit,
                lot.grade,
                lot.location,

                u.full_name AS buyer_name,
                u.email AS buyer_email,
                u.phone AS buyer_phone,
                u.city AS buyer_city

            FROM offers o

            JOIN listings l
                ON l.id = o.listing_id

            JOIN lots lot
                ON lot.id = l.lot_id

            JOIN users u
                ON u.id = o.buyer_id

            WHERE l.farmer_id = %s

            ORDER BY
                CASE
                    WHEN o.status = 'pending' THEN 1
                    WHEN o.status = 'accepted' THEN 2
                    WHEN o.status = 'countered' THEN 3
                    WHEN o.status = 'rejected' THEN 4
                    ELSE 5
                END,
                o.created_at DESC
            """,
            (farmer_id,),
        )

        offers = cursor.fetchall()

        for offer in offers:

            if offer.get("created_at"):
                offer["created_at"] = (
                    offer["created_at"]
                    .strftime("%Y-%m-%d %H:%M")
                )

        pending_count = sum(
            1
            for offer in offers
            if offer["status"] == "pending"
        )

        accepted_count = sum(
            1
            for offer in offers
            if offer["status"] == "accepted"
        )

        rejected_count = sum(
            1
            for offer in offers
            if offer["status"] == "rejected"
        )

        return render_template(
            "farmer_offers.html",
            offers=offers,
            pending_count=pending_count,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# FARMER - ACCEPT OFFER
# =========================================================

@offers_bp.post("/<int:offer_id>/accept")
@farmer_required
def accept_offer(offer_id):

    farmer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                o.id,
                o.listing_id,
                o.status,
                l.lot_id,
                l.status AS listing_status

            FROM offers o

            JOIN listings l
                ON l.id = o.listing_id

            WHERE o.id = %s
              AND l.farmer_id = %s
            FOR UPDATE
            """,
            (
                offer_id,
                farmer_id,
            ),
        )

        offer = cursor.fetchone()

        if not offer:
            return "Offer not found.", 404

        if offer["status"] != "pending":
            return (
                "Only pending offers can be accepted.",
                400,
            )

        if offer["listing_status"] != "active":
            return (
                "This listing is no longer active.",
                400,
            )

        # Accept selected offer
        cursor.execute(
            """
            UPDATE offers
            SET status = 'accepted'
            WHERE id = %s
            """,
            (offer_id,),
        )

        # Reject other pending offers
        cursor.execute(
            """
            UPDATE offers
            SET status = 'rejected'
            WHERE listing_id = %s
              AND id <> %s
              AND status = 'pending'
            """,
            (
                offer["listing_id"],
                offer_id,
            ),
        )

        # Listing becomes paused
        cursor.execute(
            """
            UPDATE listings
            SET status = 'paused'
            WHERE id = %s
            """,
            (offer["listing_id"],),
        )

        # Lot becomes matched
        cursor.execute(
            """
            UPDATE lots
            SET status = 'matched'
            WHERE id = %s
            """,
            (offer["lot_id"],),
        )

        conn.commit()

        return redirect(
            url_for(
                "offers.farmer_offers"
            )
        )

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


# =========================================================
# FARMER - REJECT OFFER
# =========================================================

@offers_bp.post("/<int:offer_id>/reject")
@farmer_required
def reject_offer(offer_id):

    farmer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                o.id,
                o.status

            FROM offers o

            JOIN listings l
                ON l.id = o.listing_id

            WHERE o.id = %s
              AND l.farmer_id = %s
            """,
            (
                offer_id,
                farmer_id,
            ),
        )

        offer = cursor.fetchone()

        if not offer:
            return "Offer not found.", 404

        if offer["status"] != "pending":
            return (
                "Only pending offers can be rejected.",
                400,
            )

        cursor.execute(
            """
            UPDATE offers
            SET status = 'rejected'
            WHERE id = %s
            """,
            (offer_id,),
        )

        conn.commit()

        return redirect(
            url_for(
                "offers.farmer_offers"
            )
        )

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()
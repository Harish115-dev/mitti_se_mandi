from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)

from app.db.database import get_connection


transactions_bp = Blueprint(
    "transactions",
    __name__,
    url_prefix="/transactions",
)


# =========================================================
# AUTH HELPERS
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


def buyer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("user_role") != "buyer":
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped


# =========================================================
# FARMER - ORDERS / SALES
# =========================================================

@transactions_bp.route("/farmer")
@farmer_required
def farmer_transactions():

    farmer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                t.id AS transaction_id,
                t.offer_id,
                t.quantity,
                t.agreed_price,
                t.total_amount,
                t.status AS transaction_status,
                t.created_at,
                t.updated_at,

                o.status AS offer_status,
                o.message AS offer_message,

                l.id AS listing_id,
                l.title AS listing_title,

                lot.crop_name,
                lot.variety,
                lot.grade,
                lot.quantity_unit,
                lot.market_name,
                lot.location,

                u.id AS buyer_id,
                u.full_name AS buyer_name,
                u.email AS buyer_email,
                u.phone AS buyer_phone,
                u.city AS buyer_city,
                u.state AS buyer_state,

                p.id AS payment_id,
                p.amount AS payment_amount,
                p.payment_reference,
                p.status AS payment_status,
                p.paid_at

            FROM transactions t

            JOIN offers o
                ON o.id = t.offer_id

            JOIN listings l
                ON l.id = o.listing_id

            JOIN lots lot
                ON lot.id = l.lot_id

            JOIN users u
                ON u.id = t.buyer_id

            LEFT JOIN payments p
                ON p.transaction_id = t.id

            WHERE t.farmer_id = %s

            ORDER BY t.created_at DESC
            """,
            (farmer_id,),
        )

        transactions = cursor.fetchall()

        return render_template(
            "farmer_transactions.html",
            transactions=transactions,
        )

    finally:

        cursor.close()
        conn.close()


# =========================================================
# BUYER - ORDERS / PURCHASES
# =========================================================

@transactions_bp.route("/buyer")
@buyer_required
def buyer_transactions():

    buyer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                t.id AS transaction_id,
                t.offer_id,
                t.quantity,
                t.agreed_price,
                t.total_amount,
                t.status AS transaction_status,
                t.created_at,
                t.updated_at,

                o.status AS offer_status,
                o.message AS offer_message,

                l.id AS listing_id,
                l.title AS listing_title,

                lot.crop_name,
                lot.variety,
                lot.grade,
                lot.quantity_unit,
                lot.market_name,
                lot.location,

                u.id AS farmer_id,
                u.full_name AS farmer_name,
                u.email AS farmer_email,
                u.phone AS farmer_phone,
                u.city AS farmer_city,
                u.state AS farmer_state,

                p.id AS payment_id,
                p.amount AS payment_amount,
                p.payment_reference,
                p.status AS payment_status,
                p.paid_at

            FROM transactions t

            JOIN offers o
                ON o.id = t.offer_id

            JOIN listings l
                ON l.id = o.listing_id

            JOIN lots lot
                ON lot.id = l.lot_id

            JOIN users u
                ON u.id = t.farmer_id

            LEFT JOIN payments p
                ON p.transaction_id = t.id

            WHERE t.buyer_id = %s

            ORDER BY t.created_at DESC
            """,
            (buyer_id,),
        )

        transactions = cursor.fetchall()

        return render_template(
            "buyer_transactions.html",
            transactions=transactions,
        )

    finally:

        cursor.close()
        conn.close()
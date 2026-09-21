import os
from datetime import datetime
from decimal import Decimal
from functools import wraps

import razorpay

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.db.database import get_connection


# =========================================================
# BLUEPRINT
# =========================================================

payments_bp = Blueprint(
    "payments",
    __name__,
    url_prefix="/payments",
)


# =========================================================
# RAZORPAY CLIENT
# =========================================================

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise RuntimeError(
        "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET "
        "must be set in the environment."
    )


razorpay_client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET,
    )
)


# =========================================================
# RAZORPAY PAYMENT LIMIT
# =========================================================

# Maximum transaction value supported by Razorpay:
# ₹25,00,000
MAX_RAZORPAY_AMOUNT_RUPEES = Decimal("2500000")

MAX_RAZORPAY_AMOUNT_PAISE = int(
    MAX_RAZORPAY_AMOUNT_RUPEES * Decimal("100")
)


# =========================================================
# BUYER AUTH
# =========================================================

def buyer_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("auth.login")
            )

        if session.get("user_role") != "buyer":
            return redirect(
                url_for("auth.login")
            )

        return view(*args, **kwargs)

    return wrapped


# =========================================================
# CREATE PAYMENT ORDER
# =========================================================

@payments_bp.route(
    "/create/<int:transaction_id>",
    methods=["GET"],
)
@buyer_required
def create_payment(transaction_id):

    buyer_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # Fetch transaction + payment
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                t.id AS transaction_id,
                t.offer_id,
                t.buyer_id,
                t.farmer_id,
                t.quantity,
                t.agreed_price,
                t.total_amount,
                t.status AS transaction_status,

                o.status AS offer_status,

                lot.crop_name,
                lot.variety,
                lot.quantity_unit,

                p.id AS payment_id,
                p.amount AS payment_amount,
                p.status AS payment_status,
                p.razorpay_order_id

            FROM transactions t

            JOIN offers o
                ON o.id = t.offer_id

            JOIN listings l
                ON l.id = o.listing_id

            JOIN lots lot
                ON lot.id = l.lot_id

            JOIN payments p
                ON p.transaction_id = t.id

            WHERE t.id = %s
              AND t.buyer_id = %s

            LIMIT 1
            """,
            (
                transaction_id,
                buyer_id,
            ),
        )

        transaction = cursor.fetchone()

        if not transaction:
            return "Transaction not found.", 404


        # -------------------------------------------------
        # Transaction must still be payable
        # -------------------------------------------------

        if transaction["transaction_status"] != "pending":

            return (
                "This transaction is not available for payment.",
                400,
            )


        # -------------------------------------------------
        # Payment must not already be paid
        # -------------------------------------------------

        if transaction["payment_status"] == "paid":

            return (
                "This transaction has already been paid.",
                400,
            )


        # -------------------------------------------------
        # Calculate amount
        # -------------------------------------------------

        amount_rupees = Decimal(
            str(transaction["total_amount"])
        )

        amount_paise = int(
            (amount_rupees * Decimal("100")).quantize(
                Decimal("1")
            )
        )


        # -------------------------------------------------
        # Validate amount
        # -------------------------------------------------

        if amount_paise <= 0:

            return (
                "Invalid payment amount.",
                400,
            )


        # -------------------------------------------------
        # HIGH-VALUE PAYMENT CHECK
        # -------------------------------------------------

        if amount_paise > MAX_RAZORPAY_AMOUNT_PAISE:

            return render_template(
                "payment_checkout.html",

                transaction=transaction,

                transaction_id=transaction_id,

                razorpay_key_id=RAZORPAY_KEY_ID,

                razorpay_order_id=None,

                amount_paise=amount_paise,

                payment_error=(
                    "This transaction is above the online "
                    "payment limit for Razorpay. "
                    "Please use the high-value settlement "
                    "process instead."
                ),
            )


        # -------------------------------------------------
        # Existing Razorpay order
        # -------------------------------------------------

        razorpay_order_id = (
            transaction["razorpay_order_id"]
        )


        # -------------------------------------------------
        # Check whether existing order is reusable
        # -------------------------------------------------

        if razorpay_order_id:

            try:

                existing_order = (
                    razorpay_client.order.fetch(
                        razorpay_order_id
                    )
                )

                existing_amount = int(
                    existing_order.get("amount", 0)
                )

                existing_status = (
                    existing_order.get("status")
                )


                # Only reuse a Razorpay order if:
                # 1. It is still "created"
                # 2. The amount matches exactly

                if (
                    existing_status != "created"
                    or existing_amount != amount_paise
                ):

                    razorpay_order_id = None


            except Exception:

                # If the old order cannot be fetched,
                # create a fresh order.

                razorpay_order_id = None


        # -------------------------------------------------
        # Create a NEW Razorpay order when necessary
        # -------------------------------------------------

        if not razorpay_order_id:

            order_data = {
                "amount": amount_paise,

                "currency": "INR",

                "receipt": (
                    f"txn_{transaction_id}"
                ),

                "notes": {
                    "transaction_id": str(
                        transaction_id
                    ),

                    "buyer_id": str(
                        buyer_id
                    ),

                    "offer_id": str(
                        transaction["offer_id"]
                    ),
                },
            }


            try:

                razorpay_order = (
                    razorpay_client.order.create(
                        data=order_data
                    )
                )


            except Exception as exc:

                # Keep the application from showing
                # an unhelpful Flask 500 page.

                return render_template(
                    "payment_checkout.html",

                    transaction=transaction,

                    transaction_id=transaction_id,

                    razorpay_key_id=RAZORPAY_KEY_ID,

                    razorpay_order_id=None,

                    amount_paise=amount_paise,

                    payment_error=(
                        "Razorpay could not create the "
                        "online payment order. "
                        f"Please try again. Details: {str(exc)}"
                    ),
                ), 400


            razorpay_order_id = (
                razorpay_order["id"]
            )


            # -------------------------------------------------
            # Store new Razorpay order ID
            # -------------------------------------------------

            cursor.execute(
                """
                UPDATE payments
                SET razorpay_order_id = %s
                WHERE transaction_id = %s
                """,
                (
                    razorpay_order_id,
                    transaction_id,
                ),
            )


            conn.commit()


        # -------------------------------------------------
        # Payment checkout page
        # -------------------------------------------------

        return render_template(
            "payment_checkout.html",

            transaction=transaction,

            # Explicit transaction ID
            transaction_id=transaction_id,

            razorpay_key_id=RAZORPAY_KEY_ID,

            razorpay_order_id=razorpay_order_id,

            amount_paise=amount_paise,

            payment_error=None,
        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# VERIFY PAYMENT
# =========================================================

@payments_bp.route(
    "/verify",
    methods=["POST"],
)
@buyer_required
def verify_payment():

    buyer_id = session["user_id"]


    # -----------------------------------------------------
    # Read form values
    # -----------------------------------------------------

    transaction_id = (
        request.form.get("transaction_id")
        or request.args.get("transaction_id")
        or ""
    ).strip()


    razorpay_order_id = (
        request.form.get("razorpay_order_id")
        or ""
    ).strip()


    razorpay_payment_id = (
        request.form.get("razorpay_payment_id")
        or ""
    ).strip()


    razorpay_signature = (
        request.form.get("razorpay_signature")
        or ""
    ).strip()


    # -----------------------------------------------------
    # Validate transaction ID
    # -----------------------------------------------------

    if not transaction_id:

        return (
            "Transaction ID is required.",
            400,
        )


    try:

        transaction_id = int(
            transaction_id
        )

    except (TypeError, ValueError):

        return (
            "Invalid transaction ID.",
            400,
        )


    # -----------------------------------------------------
    # Validate Razorpay data
    # -----------------------------------------------------

    if not razorpay_order_id:

        return (
            "Razorpay order ID is required.",
            400,
        )


    if not razorpay_payment_id:

        return (
            "Razorpay payment ID is required.",
            400,
        )


    if not razorpay_signature:

        return (
            "Razorpay signature is required.",
            400,
        )


    conn = get_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # -------------------------------------------------
        # Fetch transaction/payment
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                t.id AS transaction_id,
                t.buyer_id,
                t.status AS transaction_status,

                p.id AS payment_id,
                p.amount,
                p.status AS payment_status,
                p.razorpay_order_id

            FROM transactions t

            JOIN payments p
                ON p.transaction_id = t.id

            WHERE t.id = %s
              AND t.buyer_id = %s

            FOR UPDATE
            """,
            (
                transaction_id,
                buyer_id,
            ),
        )


        payment = cursor.fetchone()


        if not payment:

            return (
                "Payment record not found.",
                404,
            )


        # -------------------------------------------------
        # Order ID must match database
        # -------------------------------------------------

        if (
            payment["razorpay_order_id"]
            != razorpay_order_id
        ):

            return (
                "Razorpay order does not match "
                "the transaction.",
                400,
            )


        # -------------------------------------------------
        # Don't process payment twice
        # -------------------------------------------------

        if payment["payment_status"] == "paid":

            return redirect(
                url_for(
                    "transactions.buyer_transactions"
                )
            )


        # -------------------------------------------------
        # Verify Razorpay signature
        # -------------------------------------------------

        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_order_id":
                    razorpay_order_id,

                "razorpay_payment_id":
                    razorpay_payment_id,

                "razorpay_signature":
                    razorpay_signature,
            }
        )


        # -------------------------------------------------
        # Mark payment as paid
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE payments

            SET
                razorpay_payment_id = %s,
                payment_reference = %s,
                status = 'paid',
                paid_at = %s

            WHERE transaction_id = %s
            """,
            (
                razorpay_payment_id,
                razorpay_payment_id,
                datetime.now(),
                transaction_id,
            ),
        )


        # -------------------------------------------------
        # Confirm transaction
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE transactions

            SET status = 'confirmed'

            WHERE id = %s
              AND buyer_id = %s
              AND status = 'pending'
            """,
            (
                transaction_id,
                buyer_id,
            ),
        )


        conn.commit()


        # -------------------------------------------------
        # Return to buyer orders
        # -------------------------------------------------

        return redirect(
            url_for(
                "transactions.buyer_transactions"
            )
        )


    except Exception:

        conn.rollback()

        raise


    finally:

        cursor.close()
        conn.close()
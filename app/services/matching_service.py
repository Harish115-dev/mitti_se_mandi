from app.db.database import get_connection


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().casefold()


def normalize_grade(value):
    value = normalize(value)

    if value.startswith("grade "):
        value = value[6:].strip()

    return value


def location_matches(preferred_location, listing_location):
    if not preferred_location:
        return True

    preferred = normalize(preferred_location)
    actual = normalize(listing_location)

    return preferred in actual


def get_buyer_matches(buyer_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                br.id AS requirement_id,
                br.crop_name AS required_crop,
                br.variety AS required_variety,
                br.min_quantity,
                br.max_quantity,
                br.quantity_unit,
                br.required_grade,
                br.preferred_location,
                br.max_price,

                l.id AS listing_id,
                l.lot_id,
                l.farmer_id,
                l.title AS listing_title,
                l.description AS listing_description,
                l.asking_price,
                l.status AS listing_status,

                lot.crop_name,
                lot.variety,
                lot.quantity,
                lot.quantity_unit AS lot_quantity_unit,
                lot.grade,
                lot.location AS lot_location,
                lot.market_name,
                lot.status AS lot_status,

                u.full_name AS farmer_name,
                u.phone AS farmer_phone,
                u.city AS farmer_city,
                u.state AS farmer_state,
                u.address AS farmer_address

            FROM buyer_requirements br

            JOIN listings l
                ON l.status = 'active'

            JOIN lots lot
                ON lot.id = l.lot_id
               AND lot.status = 'published'

            JOIN users u
                ON u.id = l.farmer_id
               AND u.role = 'farmer'

            WHERE br.buyer_id = %s
              AND br.status = 'active'
              AND LOWER(TRIM(br.crop_name))
                  = LOWER(TRIM(lot.crop_name))

            ORDER BY
                br.created_at DESC,
                l.created_at DESC
            """,
            (buyer_id,),
        )

        candidates = cursor.fetchall()

        matches = []

        for candidate in candidates:

            checks = []

            listing_quantity = float(
                candidate["quantity"]
            )

            listing_price = float(
                candidate["asking_price"]
            )

            listing_unit = (
                candidate["lot_quantity_unit"]
                or "quintal"
            )

            
            # Quantity
          

            quantity_ok = True

            if candidate["min_quantity"] is not None:
                quantity_ok = (
                    quantity_ok
                    and listing_quantity
                    >= float(candidate["min_quantity"])
                )

            if candidate["max_quantity"] is not None:
                quantity_ok = (
                    quantity_ok
                    and listing_quantity
                    <= float(candidate["max_quantity"])
                )

            checks.append(
                {
                    "name": "Quantity",
                    "passed": quantity_ok,
                }
            )


         
            # Grade
        

            required_grade = candidate[
                "required_grade"
            ]

            if required_grade:
                grade_ok = (
                    normalize_grade(
                        candidate["grade"]
                    )
                    ==
                    normalize_grade(
                        required_grade
                    )
                )
            else:
                grade_ok = True

            checks.append(
                {
                    "name": "Grade",
                    "passed": grade_ok,
                }
            )


           
            # Price
           

            if candidate["max_price"] is not None:

                price_ok = (
                    listing_price
                    <= float(candidate["max_price"])
                )

            else:
                price_ok = True

            checks.append(
                {
                    "name": "Price",
                    "passed": price_ok,
                }
            )


           
            # Location
           

            listing_location = (
                candidate["lot_location"]
                or candidate["farmer_city"]
                or candidate["farmer_state"]
                or ""
            )

            location_ok = location_matches(
                candidate["preferred_location"],
                listing_location,
            )

            checks.append(
                {
                    "name": "Location",
                    "passed": location_ok,
                }
            )


           
            # Match score
           

            passed = sum(
                1
                for check in checks
                if check["passed"]
            )

            total = len(checks)

            match_percentage = round(
                (passed / total) * 100
            )


            if match_percentage == 100:

                match_status = "Full Match"

            elif passed > 0:

                match_status = "Partial Match"

            else:

                match_status = "Low Match"


           
            # Reasons
           

            reasons = []

            for check in checks:

                if check["passed"]:

                    reasons.append(
                        f"{check['name']} matches"
                    )

                else:

                    reasons.append(
                        f"{check['name']} does not match"
                    )


           
            # Result
           

            matches.append(
                {
                    "requirement_id":
                        candidate["requirement_id"],

                    "listing_id":
                        candidate["listing_id"],

                    "lot_id":
                        candidate["lot_id"],

                    "farmer_id":
                        candidate["farmer_id"],

                    "required_crop":
                        candidate["required_crop"],

                    "required_variety":
                        candidate["required_variety"],

                    "crop_name":
                        candidate["crop_name"],

                    "variety":
                        candidate["variety"],

                    "quantity":
                        listing_quantity,

                    "quantity_unit":
                        listing_unit,

                    "grade":
                        candidate["grade"],

                    "expected_price":
                        listing_price,

                    "farmer_name":
                        candidate["farmer_name"],

                    "farmer_phone":
                        candidate["farmer_phone"],

                    "farmer_city":
                        candidate["farmer_city"],

                    "farmer_state":
                        candidate["farmer_state"],

                    "location":
                        listing_location,

                    "market_name":
                        candidate["market_name"],

                    "listing_title":
                        candidate["listing_title"],

                    "listing_description":
                        candidate["listing_description"],

                    "match_percentage":
                        match_percentage,

                    "match_status":
                        match_status,

                    "reasons":
                        reasons,

                    "checks":
                        checks,
                }
            )


        matches.sort(
            key=lambda item: (
                item["match_percentage"],
                item["listing_id"],
            ),
            reverse=True,
        )

        return matches

    finally:
        cursor.close()
        conn.close()
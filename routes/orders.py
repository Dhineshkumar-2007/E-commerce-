from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify
)

import json

from utils.db import get_db


orders_bp = Blueprint(
    "orders",
    __name__
)


# ===========================
# CHECKOUT
# ===========================

@orders_bp.route("", methods=["GET"])
def checkout():

    # Check login
    if "id" not in session:
        return redirect(url_for("auth.login_page"))

    customer_id = session["id"]

    # Get cart
    cart = session.get("cart", [])

    if not cart:
        return redirect(url_for("cart.cart"))

    # Database connection
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # ===========================
    # GET USER
    # ===========================

    cursor.execute("""
        SELECT
            id,
            name,
            phone
        FROM users
        WHERE id = %s
    """, (customer_id,))

    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        return "User not found", 404


    # ===========================
    # GET SAVED ADDRESSES
    # ===========================

    cursor.execute("""
        SELECT
            id,
            house_no,
            street,
            city,
            state,
            pincode,
            is_default
        FROM addresses
        WHERE user_id = %s
        ORDER BY is_default DESC, id DESC
    """, (customer_id,))

    addresses = cursor.fetchall()


    # ===========================
    # CALCULATE TOTAL
    # ===========================

    grand_total = 0

    for item in cart:

        grand_total += (
            float(item["mrp"]) *
            int(item["quantity"])
        )

    carttotal = len(cart)


    # ===========================
    # CLOSE DATABASE
    # ===========================

    cursor.close()
    db.close()


    # ===========================
    # SEND TO TEMPLATE
    # ===========================

    return render_template(
        "order.html",
        user=user,
        addresses=addresses,
        cart=cart,
        carttotal=carttotal,
        grand_total=grand_total
    )


# ===========================
# PLACE ORDER
# ===========================

@orders_bp.route("/place-order", methods=["POST"])
def place_order():

    # ===========================
    # LOGIN CHECK
    # ===========================

    if "id" not in session:
        return redirect(url_for("auth.login_page"))

    customer_id = session["id"]


    # ===========================
    # GET CART
    # ===========================

    cart = session.get("cart", [])

    if not cart:
        return redirect(url_for("cart.cart"))


    # ===========================
    # GET FORM DATA
    # ===========================

    address_type = request.form.get("address_type")
    address_id = request.form.get("address_id")

    payment_method = request.form.get(
        "payment_method",
        "COD"
    )


    # ===========================
    # ONLY COD
    # ===========================

    if payment_method != "COD":
        return "Invalid payment method", 400


    # ===========================
    # DATABASE CONNECTION
    # ===========================

    db = get_db()
    cursor = db.cursor(dictionary=True)


    # ===========================
    # GET USER
    # ===========================

    cursor.execute("""
        SELECT
            id,
            name,
            phone
        FROM users
        WHERE id = %s
    """, (customer_id,))

    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        return "User not found", 404


    # ===========================
    # ADDRESS
    # ===========================

    if address_type == "saved":

        if not address_id:
            cursor.close()
            db.close()
            return "Please select an address", 400


        cursor.execute("""
            SELECT
                house_no,
                street,
                city,
                state,
                pincode
            FROM addresses
            WHERE id = %s
            AND user_id = %s
        """, (address_id, customer_id))

        address = cursor.fetchone()

        if not address:
            cursor.close()
            db.close()
            return "Address not found", 404


    elif address_type == "new":

        house_no = request.form.get(
            "house_no",
            ""
        ).strip()

        street = request.form.get(
            "street",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        state = request.form.get(
            "state",
            ""
        ).strip()

        pincode = request.form.get(
            "pincode",
            ""
        ).strip()


        # ===========================
        # VALIDATE ADDRESS
        # ===========================

        if not all([
            house_no,
            street,
            city,
            state,
            pincode
        ]):

            cursor.close()
            db.close()

            return "Please fill all address fields", 400


        if not pincode.isdigit() or len(pincode) != 6:

            cursor.close()
            db.close()

            return "Invalid pincode", 400


        # ===========================
        # SAVE NEW ADDRESS
        # ===========================

        cursor.execute("""
            INSERT INTO addresses
            (
                user_id,
                house_no,
                street,
                city,
                state,
                pincode,
                is_default
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            customer_id,
            house_no,
            street,
            city,
            state,
            pincode,
            0
        ))


        # Address used for this order

        address = {
            "house_no": house_no,
            "street": street,
            "city": city,
            "state": state,
            "pincode": pincode
        }


    else:

        cursor.close()
        db.close()

        return "Please select a delivery address", 400


    # ===========================
    # DELIVERY ADDRESS
    # ===========================

    delivery_address = {

        "name": user["name"],

        "phone": user["phone"],

        "house_no": address["house_no"],

        "street": address["street"],

        "city": address["city"],

        "state": address["state"],

        "pincode": address["pincode"]
    }


    # ===========================
    # CALCULATE TOTAL
    # ===========================

    grand_total = 0

    for item in cart:

        grand_total += (
            float(item["mrp"]) *
            int(item["quantity"])
        )


    # ===========================
    # CREATE ORDER
    # ===========================

    cursor.execute("""
        INSERT INTO orders
        (
            customer_id,
            total_amount,
            payment_status,
            order_status,
            delivery_address
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """, (
        customer_id,
        grand_total,
        "PENDING",
        "PLACED",
        json.dumps(delivery_address)
    ))


    order_id = cursor.lastrowid


    # ===========================
    # COMMIT
    # ===========================

    db.commit()


    # ===========================
    # CLOSE DATABASE
    # ===========================

    cursor.close()
    db.close()


    # ===========================
    # CLEAR CART
    # ===========================

    session.pop("cart", None)


    # ===========================
    # REDIRECT
    # ===========================

    return redirect(
        url_for("orders.my_orders")
    )


# ===========================
# MY ORDERS
# ===========================

@orders_bp.route("/my-orders")
def my_orders():

    # ===========================
    # LOGIN CHECK
    # ===========================

    if "id" not in session:
        return redirect(url_for("auth.login_page"))

    cart = session.get("cart", [])
    carttotal=len(cart)
    customer_id = session["id"]


    # ===========================
    # DATABASE
    # ===========================

    db = get_db()
    cursor = db.cursor(dictionary=True)


    cursor.execute("""
        SELECT
            id,
            total_amount,
            payment_status,
            order_status,
            delivery_address,
            placed_at,
            delivered_at
        FROM orders
        WHERE customer_id = %s
        ORDER BY placed_at DESC
    """, (customer_id,))


    orders = cursor.fetchall()


    cursor.close()
    db.close()


    # ===========================
    # CONVERT JSON ADDRESS
    # ===========================

    for order in orders:

        if order["delivery_address"]:

            if isinstance(
                order["delivery_address"],
                str
            ):

                order["delivery_address"] = json.loads(
                    order["delivery_address"]
                )


    # ===========================
    # TEMPLATE
    # ===========================

    return render_template(
        "my_orders.html",
        orders=orders,carttotal=carttotal
    )


# ===========================
# VENDOR ORDERS
# ===========================

@orders_bp.route("/vendor-orders")
def vendor_orders():

    # ===========================
    # LOGIN CHECK
    # ===========================

    if "id" not in session:
        return redirect(url_for("auth.login_page"))


    # ===========================
    # ROLE CHECK
    # ===========================

    if session.get("role") != "VENDOR":
        return "Access Denied", 403


    return render_template(
        "vendor_orders.html"
    )
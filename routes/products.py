
from flask import Blueprint, render_template, request, session, redirect, url_for

from utils.db import get_db


product_bp = Blueprint(
    "products",
    __name__
)


# ===========================
# PRODUCTS PAGE
# ===========================

@product_bp.route("")
def get_products():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    print("SESSION:", dict(session))
    print("ROLE:", session.get("role"))

    cursor.execute("""
        SELECT
            id,
            name,
            description,
            mrp
        FROM products
    """)

    products = cursor.fetchall()

    # Cart is stored in session
    cart = session.get("cart", [])

    cart_total = len(cart)

    cart_ids = [
        item["id"]
        for item in cart
    ]

    return render_template(
        "product.html",
        products=products,
        cart_ids=cart_ids,
        cart_total=cart_total
    )


# ===========================
# ADD PRODUCT PAGE
# ===========================

@product_bp.route("/add-product")
def add_product():

    # User must be logged in
    if "id" not in session:
        return redirect(url_for("auth.login_page"))

    # Only vendors can add products
    if session.get("role") != "VENDOR":
        return "Access Denied", 403

    return render_template("add_product.html")


# ===========================
# ADD PRODUCT
# ===========================

@product_bp.route("/add_product", methods=["POST"])
def add_product_post():

    # User must be logged in
    if "id" not in session:
        return redirect(url_for("auth.login_page"))

    # Only vendors can add products
    if session.get("role") != "VENDOR":
        return "Access Denied", 403

    db = get_db()
    cursor = db.cursor()

    vendor_id = session["id"]

    name = request.form.get("name")
    category_id = request.form.get("category_id")
    description = request.form.get("description")

    # Base price
    try:
        base_price = float(
            request.form.get("base_price", 0)
        )
    except (ValueError, TypeError):
        base_price = 0

    # MRP
    try:
        mrp = float(
            request.form.get("mrp", base_price)
        )
    except (ValueError, TypeError):
        mrp = base_price

    # Stock
    try:
        stock = int(
            request.form.get("stock", 0)
        )
    except (ValueError, TypeError):
        stock = 0

    # GST
    try:
        gst_rate = float(
            request.form.get("gst_rate", 0)
        )
    except (ValueError, TypeError):
        gst_rate = 0

    status = request.form.get(
        "status",
        "ACTIVE"
    )

    sql = """
        INSERT INTO products
        (
            vendor_id,
            name,
            category_id,
            description,
            base_price,
            mrp,
            stock,
            gst_rate,
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
            %s
        )
    """

    cursor.execute(
        sql,
        (
            vendor_id,
            name,
            category_id,
            description,
            base_price,
            mrp,
            stock,
            gst_rate,
            status
        )
    )

    db.commit()

    return redirect(
        url_for("products.my_products")
    )


# ===========================
# MY PRODUCTS
# ===========================

@product_bp.route("/my-products")
def my_products():

    # User must be logged in
    if "id" not in session:
        return redirect(
            url_for("auth.login_page")
        )

    # Only vendors can access
    if session.get("role") != "VENDOR":
        return "Access Denied", 403

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            description,
            mrp,
            stock,
            status
        FROM products
        WHERE vendor_id = %s
    """, (session["id"],))

    products = cursor.fetchall()

    return render_template(
        "my_products.html",
        products=products
    )


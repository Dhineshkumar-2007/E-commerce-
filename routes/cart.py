
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for

from utils.db import get_db


cart_bp = Blueprint(
    "cart",
    __name__
)



# ===========================
# ADD TO CART
# (Stored in Session)
# ===========================

@cart_bp.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    print("SESSION:", dict(session))
    print("USER ID:", session.get("id"))
    

    # User must be logged in
    if "id" not in session:
        return redirect(url_for("auth.login_page"))

    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            description,
            mrp
        FROM products
        WHERE id=%s
    """, (product_id,))

    product = cursor.fetchone()

    if not product:
        return "Product Not Found"

    cart = session.get("cart", [])

    product_found = False

    for item in cart:

        if item["id"] == product["id"]:

            item["quantity"] += 1

            product_found = True

            break

    if not product_found:

        product["quantity"] = 1

        cart.append(product)

    session["cart"] = cart

    return "ok"

#update cart 
@cart_bp.route("/cart/update-cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):

    # Check if user is logged in
    if "id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 401

    # Get JSON data from JavaScript
    data = request.get_json()

    quantity = data.get("quantity")

    # Validate quantity
    if quantity is None:
        return jsonify({
            "success": False,
            "message": "Quantity is required"
        }), 400

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid quantity"
        }), 400

    # Quantity cannot be less than 1
    if quantity < 1:
        return jsonify({
            "success": False,
            "message": "Invalid quantity"
        }), 400

    # Get cart from session
    cart = session.get("cart", [])

    # Find product
    for item in cart:

        if int(item["id"]) == product_id:

            item["quantity"] = quantity

            break

    else:
        return jsonify({
            "success": False,
            "message": "Product not found in cart"
        }), 404

    # Tell Flask session that cart changed
    session["cart"] = cart
    session.modified = True

    # Calculate new total
    total = sum(
        float(item["mrp"]) * int(item["quantity"])
        for item in cart
    )
   
    return jsonify({
        "success": True,
        "quantity": quantity,
        "total": total
    })


# ===========================
# CART PAGE
# ===========================
@cart_bp.route("")
def cart():

    cart = session.get("cart", [])
    

    grand_total = 0

    for item in cart:

        item["subtotal"]=float(item["mrp"])*int(item["quantity"])    
        grand_total += item["subtotal"]
    carttotal=len(cart)
    return render_template(
        "cartpage.html",
        cart=cart,
        grand_total=grand_total,carttotal=carttotal
    )




# ===========================
# REMOVE FROM CART
# ===========================

@cart_bp.route("/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", [])

    cart = [
        item
        for item in cart
        if int(item["id"]) != product_id
    ]

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart.cart"))

# ===========================
# CLEAR CART
# ===========================

@cart_bp.route("/clear-cart")
def clear_cart():

    session.pop("cart", None)

    return redirect(url_for("cart.cart"))

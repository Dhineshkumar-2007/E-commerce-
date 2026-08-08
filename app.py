import os
import mysql.connector
import math,random
from dotenv import load_dotenv
from werkzeug import security

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)

app = Flask(__name__)
app.secret_key = "my_secret_key"


#OTP 
def generateOTP():
    digits="1234567890"
    OTP=""
    for i in range(4):
        OTP+=digits[math.floor(random.random()*10)]
    return OTP



#Loading .env file
load_dotenv()
# ===========================
# DATABASE CONFIG
# ===========================

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_ca=os.getenv("DB_SSL_CA")
)

# ===========================
# HOME PAGE
# ===========================

@app.route("/")
def home():

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, description, mrp
        FROM products
        LIMIT 4
    """)

    products = cursor.fetchall()

     # Get cart from session
    cart = session.get("cart", [])

    # Get only product IDs
    cart_ids = [item["id"] for item in cart]

    return render_template(
        "home.html",
        products=products,cart_ids=cart_ids
    )





# ===========================
# SEARCH PRODUCT
# ===========================

@app.route("/search")
def search_product():

    search = request.args.get("search", "")

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, description, mrp
        FROM products
        WHERE name LIKE %s
    """, ("%" + search + "%",))

    products = cursor.fetchall()

    return jsonify(products)


# ===========================
# REGISTER PAGE
# ===========================

@app.route("/register")
def register_page():

    return render_template("register.html")


# ===========================
# REGISTER USER
# ===========================

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]
    role = request.form["role"]

    password_hash=security.generate_password_hash(password)
    
    cursor = db.cursor()

    sql = """
    INSERT INTO users
    (
        name,
        email,
        phone,
        password_hash,
        role
    )

    VALUES
    (
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
            name,
            email,
            phone,
            password_hash,
            role
        )
    )


  

    db.commit()

    return render_template("success.html")


# ===========================
# LOGIN PAGE
# ===========================

@app.route("/login")
def login_page():

    return render_template("login.html")


# ===========================
# LOGIN CHECK
# ===========================

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    cursor = db.cursor()

    sql = """
    SELECT
        id,
        name,
        role,
        password_hash

    FROM users

    WHERE
        email=%s
        
    """
    cursor.execute(sql, (email, ))
    

    user = cursor.fetchone()

    if user  and security.check_password_hash(user[3],password) :

        session["id"] = user[0]
        session["name"] = user[1]
        session["role"] = user[2]

        if user[2] == "CUSTOMER":
            return redirect(url_for("home"))

        elif user[2] == "VENDOR":
            return redirect(url_for("vendor_dashboard"))

        elif user[2] == "ADMIN":
            return redirect(url_for("admin_dashboard"))

    return render_template(
        "login.html",
        error="Invalid Email or Password"
    )
    


# ===========================
# LOGOUT
# ===========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login_page"))

# ===========================
# CUSTOMER DASHBOARD
# ===========================

@app.route("/customer")
def customer_dashboard():

    if "id" not in session:
        return redirect(url_for("login_page"))

    if session["role"] != "CUSTOMER":
        return "Access Denied", 403

    return render_template("customer_dashboard.html")


# ===========================
# VENDOR DASHBOARD
# ===========================

@app.route("/vendor")
def vendor_dashboard():

    if "id" not in session : 
        return redirect(url_for("login_page"))
    elif session["role"] != "VENDOR" :
        return "acces denied",403
    
    return render_template("vendor_dashboard.html")


# ===========================
# ADMIN DASHBOARD
# ===========================

@app.route("/admin")
def admin_dashboard():

    if "id" not in session:
        return redirect(url_for("login_page"))

    if session["role"] != "ADMIN":
        return "Access Denied", 403

    return render_template("admin_page.html")


# ===========================
# PRODUCTS PAGE
# ===========================

@app.route("/products")
def get_products():

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            description,
            mrp
        FROM products
    """)

    products = cursor.fetchall()

    cart = session.get("cart", [])

    cart_ids = [item["id"] for item in cart]

    return render_template(
        "product.html",
        products=products,cart_ids=cart_ids
    )


# ===========================
# ADD TO CART
# (Stored in Session)
# ===========================

@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

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


# ===========================
# CART PAGE
# ===========================

@app.route("/cart")
def cart():

    cart = session.get("cart", [])

    grand_total = 0

    for item in cart:

        grand_total += float(item["mrp"]) * int(item["quantity"])

    return render_template(
        "cartpage.html",
        cart=cart,
        total=grand_total
    )


# ===========================
# REMOVE FROM CART
# ===========================

@app.route("/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", [])

    cart = [
        item
        for item in cart
        if item["id"] != product_id
    ]

    session["cart"] = cart

    return redirect(url_for("cart"))


# ===========================
# CLEAR CART
# ===========================

@app.route("/clear-cart")
def clear_cart():

    session.pop("cart", None)

    return redirect(url_for("cart"))
# ===========================
# ADD PRODUCT PAGE
# ===========================

@app.route("/add-product")
def add_product():

    if "id" not in session:
        return redirect(url_for("login_page"))

    if session["role"] != "VENDOR":
        return "Access Denied", 403

    return render_template("add_product.html")


# ===========================
# ADD PRODUCT
# ===========================

@app.route("/add_product", methods=["POST"])
def add_product_post():

    if "id" not in session:
        return redirect(url_for("login_page"))

    if session["role"] != "VENDOR":
        return "Access Denied", 403

    vendor_id = session["id"]
    name = request.form.get("name")
    category_id = request.form.get("category_id")
    description = request.form.get("description")

    try:
        base_price = float(request.form.get("base_price", 0))
    except ValueError:
        base_price = 0

    try:
        mrp = float(request.form.get("mrp", base_price))
    except ValueError:
        mrp = base_price

    try:
        stock = int(request.form.get("stock", 0))
    except ValueError:
        stock = 0

    try:
        gst_rate = float(request.form.get("gst_rate", 0))
    except ValueError:
        gst_rate = 0

    status = request.form.get("status", "ACTIVE")

    cursor = db.cursor()

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
        %s,%s,%s,%s,%s,%s,%s,%s,%s
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

    return redirect(url_for("my_products"))


# ===========================
# MY PRODUCTS
# ===========================

@app.route("/my-products")
def my_products():

    if "id" not in session:
        return redirect(url_for("login_page"))

    if session["role"] != "VENDOR":
        return "Access Denied", 403

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


# ===========================
# VENDOR ORDERS
# ===========================

@app.route("/vendor-orders")
def vendor_orders():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    if session["role"] != "VENDOR":
        return "Access Denied", 403

    return render_template("vendor_orders.html")


# ===========================
# CHECKOUT
# ===========================

@app.route("/checkout")
def checkout():

    cart = session.get("cart", [])

    if len(cart) == 0:
        return redirect(url_for("cart"))

    # Later you can save orders into an orders table
    session.pop("cart", None)

    return render_template("success.html")


# ===========================
# RUN APP
# ===========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )

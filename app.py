import os

from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)


db = mysql.connector.connect(
host=os.getenv("DB_HOST", "localhost"),
user=os.getenv("DB_USER", "root"),
password="Sql.dk2007@14",
database=os.getenv("DB_NAME", "mydb1")
)

cursor=db.cursor()

@app.route("/")
def home():
    return render_template("home.html")



@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/register",methods=["POST"])
def register ():
    
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]
    role = request.form["role"]
    
    sql = """
    INSERT INTO users(name,email, phone, password_hash, role)
    VALUES ( %s,%s, %s, %s, %s)
    """

    cursor.execute(sql, (name,email, phone, password, role))
    db.commit()
    return render_template("success.html")

@app.route("/login")
def login_page():
    return render_template("/login.html")

 #Login check
@app.route("/login", methods=["POST"])
def login_():

    email = request.form["email"]
    password = request.form["password"]

    sql = """
    SELECT id, name, role
    FROM users
    WHERE email=%s AND password_hash=%s
    """

    cursor.execute(sql, (email, password))

    user = cursor.fetchone()

    if user:
        role = user[2]

        if role == "CUSTOMER":
            return render_template("customer_dashboard.html")

        elif role == "VENDOR":
            return render_template("vendor_dashboard.html")

    return render_template(
        "login.html",
        error="Invalid email or password!"
    )


@app.route("/customer")
def customer_dashboard():
    return render_template("customer_dashboard.html")


@app.route("/vendor")
def vendor_dashboard():
    return render_template("vendor_dashboard.html")


@app.route("/products")
def products():
    return render_template("product.html")



@app.route("/add-product")
def add_product():
    return render_template("add_product.html")


@app.route("/add_product", methods=["POST"])
def add_product_post():
    # Collect form fields matching the products table schema
    vendor_id = request.form.get("vendor_id")
    name = request.form.get("name")
    category_id = request.form.get("category_id") or None
    description = request.form.get("description")

    # Numeric/decimal fields: convert or default
    try:
        base_price = float(request.form.get("base_price", 0))
    except ValueError:
        base_price = 0.0
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
        gst_rate = 0.0

    status = request.form.get("status") or "ACTIVE"

    sql = """
    INSERT INTO products (vendor_id, name, category_id, description, base_price, mrp, stock, gst_rate, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (vendor_id, name, category_id, description, base_price, mrp, stock, gst_rate, status))
    db.commit()
    return render_template("success.html")


@app.route("/my-products")
def my_products():
    return render_template("product.html")


@app.route("/vendor-orders")
def vendor_orders():
    return "<h1>Vendor Orders Page</h1>"

if __name__=="__main__":
    app.run(debug=True)
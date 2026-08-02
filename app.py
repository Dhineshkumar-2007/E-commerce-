from flask import Flask,render_template,request,redirect,url_for
import mysql.connector

app = Flask(__name__)

db =mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sql.dk2007@14",
    database="mydb1"
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
    return "<h1>Products Page</h1>"


@app.route("/add-product")
def add_product():
    return "<h1>Add Product Page</h1>"


@app.route("/my-products")
def my_products():
    return "<h1>My Products Page</h1>"


@app.route("/vendor-orders")
def vendor_orders():
    return "<h1>Vendor Orders Page</h1>"

if __name__=="__main__":
    app.run(debug=True)
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from utils.db import get_db


auth_bp = Blueprint("auth", __name__,template_folder='/templates')



# ===========================
# REGISTER PAGE
# ===========================

@auth_bp.route("/register")
def register_page():

    return render_template("register.html")


# ===========================
# REGISTER USER
# ===========================

@auth_bp.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]
    role = request.form["role"]

    password_hash=generate_password_hash(password)
    db = get_db()
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

@auth_bp.route("/login")
def login_page():

    return render_template("login.html")


# ===========================
# LOGIN CHECK
# ===========================

@auth_bp.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

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

    print("USER:", user)

    if user and check_password_hash(user["password_hash"], password):

        session["id"] = user["id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        if user["role"] == "CUSTOMER":
            return redirect(url_for("home"))

        elif user["role"] == "VENDOR":
            return redirect(url_for("vendor_dashboard"))

        elif user["role"] == "ADMIN":
            return redirect(url_for("admin_dashboard"))

    return render_template(
        "login.html",
        error="Invalid Email or Password"
    )
    


# ===========================
# LOGOUT
# ===========================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return render_template("login.html")

# ===========================
# CUSTOMER DASHBOARD
# ===========================

@auth_bp.route("/customer")
def customer_dashboard():

    if "id" not in session:
        return redirect(url_for("auth.login_page"))

    if session["role"] != "CUSTOMER":
        return "Access Denied", 403

    return render_template("customer_dashboard.html")


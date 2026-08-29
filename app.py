from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from routes.auth import auth_bp
from routes.products import product_bp
from routes.cart import cart_bp
from routes.orders import orders_bp


from utils.db import get_db
from config import Config

app = Flask(__name__)

app.config.from_object(Config)


app.register_blueprint(auth_bp,url_prefix="/auth")
app.register_blueprint(product_bp,url_prefix="/products")
app.register_blueprint(cart_bp,url_prefix="/cart")
app.register_blueprint(orders_bp,url_prefix="/orders")




# ===========================
# HOME PAGE
# ===========================

@app.route("/")
def home():
    db = get_db()
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
    carttotal=len(cart)
    return render_template(
        "home.html",
        products=products,cart_ids=cart_ids,carttotal=carttotal
    )





# ===========================
# SEARCH PRODUCT
# ===========================

@app.route("/search")
def search_product():

    search = request.args.get("search", "")
    db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, description, mrp
        FROM products
        WHERE name LIKE %s
    """, ("%" + search + "%",))

    products = cursor.fetchall()

    return jsonify(products)



# ===========================
# VENDOR DASHBOARD
# ===========================

@app.route("/vendor")
def vendor_dashboard():

    if "id" not in session : 
        return redirect(url_for("login_page"))
    elif session["role"] != "VENDOR" :
        return "Access Denied", 403
    
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
# RUN APP
# ===========================
"""
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
"""



if __name__ == "__main__":
    app.run(debug=True)
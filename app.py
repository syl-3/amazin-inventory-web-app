from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "super-secret-key"

@app.before_request
def reset_session_on_restart():
    session.permanent = False

def get_db_connection():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    selected_category = request.args.get("category")

    if selected_category:
        products = conn.execute("SELECT * FROM products WHERE category = ? ORDER BY name ASC", (selected_category,)).fetchall()
    else:
        products = conn.execute("SELECT * FROM products ORDER BY name ASC").fetchall()

    liked_ids = set()
    if session.get("username"):
        user = conn.execute("SELECT * FROM users WHERE username = ?", (session["username"],)).fetchone()
        if user:
            liked_ids = get_user_likes(user["id"])

    conn.close()
    return render_template("index.html", products=products, session=session, liked_ids=liked_ids, selected_category=selected_category)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()

        if user:
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing_user:
            flash("Username already taken.", "error")
            conn.close()
            return redirect(url_for("signup"))

        # Default all signups to "Customer" role
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     (username, password, "Customer"))
        conn.commit()
        conn.close()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/admin")
def admin_panel():
    if session.get("role") not in ("CEO", "Manager"):
        flash("Access denied. Admins only.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products ORDER BY name ASC").fetchall()

    conn.close()

    return render_template("admin.html", products=products)

@app.route("/add_product", methods=["POST"])
def add_product():
    if session.get("role") not in ("CEO", "Manager"):
        flash("Access denied. Admins only.", "error")
        return redirect(url_for("index"))

    name = request.form["name"]
    price = float(request.form["price"])
    stock = int(request.form["stock"])

    conn = get_db_connection()
    conn.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()
    conn.close()

    flash("Product added successfully.", "success")
    return redirect(url_for("admin_panel"))

@app.route("/delete_product", methods=["POST"])
def delete_product():
    if session.get("role") not in ("CEO", "Manager"):
        flash("Access denied. Admins only.", "error")
        return redirect(url_for("index"))

    product_id = request.form.get("product_id")

    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    flash("Product deleted successfully.", "success")
    return redirect(url_for("admin_panel"))

@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if session.get("role") not in ("CEO", "Manager"):
        flash("Access denied. Admins only.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        category = request.form["category"]

        conn.execute("UPDATE products SET name = ?, price = ?, stock = ?, category = ? WHERE id = ?",
                     (name, price, stock, category, product_id))
        conn.commit()
        conn.close()

        flash("Product updated successfully.", "success")
        return redirect(url_for("admin_panel"))

    # GET request: show edit form
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("admin_panel"))

    return render_template("edit_product.html", product=product)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if session.get("role") != "Customer":
        flash("Only customers can add to cart.", "error")
        category = request.args.get("category") or request.form.get("category")
        return redirect(url_for("index", category=category) if category else url_for("index"))


    product_id = request.form["product_id"]
    product_name = request.form["product_name"]
    price = float(request.form["price"])

    cart = session.get("cart", [])

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "product_id": product_id,
            "product_name": product_name,
            "price": price,
            "quantity": 1
        })

    session["cart"] = cart
    flash(f"{product_name} added to cart!", "success")
    return redirect(url_for("index"))

@app.route("/cart")
def view_cart():
    if session.get("role") != "Customer":
        flash("Only customers can view cart.", "error")
        return redirect(url_for("index"))

    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    product_id = request.form["product_id"]
    cart = session.get("cart", [])
    cart = [item for item in cart if item["product_id"] != product_id]
    session["cart"] = cart
    flash("Item removed from cart.", "info")
    return redirect(url_for("view_cart"))

@app.route("/increment_cart", methods=["POST"])
def increment_cart_item():
    product_id = request.form["product_id"]
    cart = session.get("cart", [])
    for item in cart:
        if str(item["product_id"]) == product_id:
            item["quantity"] += 1
            break
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))

@app.route("/decrement_cart", methods=["POST"])
def decrement_cart_item():
    product_id = request.form["product_id"]
    cart = session.get("cart", [])
    for item in cart:
        if str(item["product_id"]) == product_id:
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                cart.remove(item)
            break
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))

from datetime import datetime, timedelta, timezone

@app.route("/checkout", methods=["POST"])
def checkout():
    if session.get("role") != "Customer":
        flash("Only customers can check out.", "error")
        return redirect(url_for("index"))

    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("view_cart"))

    conn = get_db_connection()
    for item in cart:
        # Validate inventory
        current = conn.execute("SELECT stock FROM products WHERE id = ?", (item["product_id"],)).fetchone()
        if not current:
            flash(f"Product with ID {item['product_id']} does not exist.", "error")
            conn.close()
            return redirect(url_for("view_cart"))
        if current["stock"] < item["quantity"]:
            left = current['stock']
            unit = "item" if left == 1 else "items"
            flash(f"Not enough stock for {item['product_name']}. Only {left} {unit} left.", "error")
            conn.close()
            return redirect(url_for("view_cart"))

    # Calculate local time
    local_offset = timedelta(hours=-5)  # adjust if you're not Central Time
    local_timezone = timezone(local_offset)
    local_now = datetime.now(local_timezone)

    user = conn.execute("SELECT * FROM users WHERE username = ?", (session["username"],)).fetchone()
    user_id = user["id"]

    for item in cart:
        current = conn.execute("SELECT stock FROM products WHERE id = ?", (item["product_id"],)).fetchone()
        new_stock = current["stock"] - item["quantity"]
        conn.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, item["product_id"]))

        # Insert into orders table, manually providing local_now
        conn.execute("""
            INSERT INTO orders (user_id, product_name, quantity, price, order_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, item["product_name"], item["quantity"], item["price"], local_now.strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    # Clear cart and flash confirmation
    session["cart"] = []
    ship_date = (local_now + timedelta(days=3)).strftime("%A, %B %d, %Y")
    flash(f"Thank you for your order! Your items will ship on {ship_date}.", "success")

    return redirect(url_for("index"))


def get_user_likes(user_id):
    conn = get_db_connection()
    rows = conn.execute("SELECT product_id FROM likes WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return {row["product_id"] for row in rows}

@app.route("/like/<int:product_id>", methods=["POST"])
def like_product(product_id):
    if session.get("role") != "Customer":
        flash("Only customers can like products.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session["username"],)).fetchone()
    conn.execute("INSERT OR IGNORE INTO likes (user_id, product_id) VALUES (?, ?)", (user["id"], product_id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/unlike/<int:product_id>", methods=["POST"])
def unlike_product(product_id):
    if session.get("role") != "Customer":
        flash("Only customers can unlike products.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session["username"],)).fetchone()
    conn.execute("DELETE FROM likes WHERE user_id = ? AND product_id = ?", (user["id"], product_id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/favorites")
def view_favorites():
    if "username" not in session:
        flash("You must be logged in to view your favorites.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session["username"],)).fetchone()

    if not user:
        conn.close()
        flash("User not found.", "error")
        return redirect(url_for("index"))

    user_id = user["id"]

    # Get product IDs from 'likes' table (not 'favorites')
    liked_rows = conn.execute("SELECT product_id FROM likes WHERE user_id = ?", (user_id,)).fetchall()
    liked_ids = [row["product_id"] for row in liked_rows]

    if liked_ids:
        placeholders = ",".join(["?"] * len(liked_ids))
        query = f"SELECT * FROM products WHERE id IN ({placeholders})"
        products = conn.execute(query, liked_ids).fetchall()
    else:
        products = []

    conn.close()
    return render_template("favorites.html", products=products)

@app.route("/my_orders")
def my_orders():
    if session.get("role") != "Customer":
        flash("Only customers can view their orders.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session["username"],)).fetchone()
    orders = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC", (user["id"],)).fetchall()
    conn.close()

    return render_template("my_orders.html", orders=orders)


@app.route("/admin/orders")
def all_orders():
    if session.get("role") != "CEO":
        flash("Access denied. CEO only.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    orders = conn.execute("""
        SELECT orders.*, users.username FROM orders
        JOIN users ON orders.user_id = users.id
        ORDER BY order_date DESC
    """).fetchall()
    conn.close()

    return render_template("all_orders.html", orders=orders)


if __name__ == "__main__":
    app.run(debug=True)

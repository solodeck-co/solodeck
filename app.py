from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3, os, json

app = Flask(__name__)
app.secret_key = "solodeck-secret-2026"

BASE = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(BASE, "database", "solodeck.db")
os.makedirs(os.path.join(BASE, "database"), exist_ok=True)

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    con = db(); c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT,
        price REAL, category TEXT, type TEXT DEFAULT 'digital',
        image_label TEXT, stock INTEGER DEFAULT 999, featured INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, name TEXT,
        items TEXT, total REAL, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        rows = [
            ("Brand Starter Kit","Logo templates, color palette, font guide, business card, email signature. Build your brand in minutes.",19.00,"Templates","digital","SD",999,1),
            ("Social Media Pack","30 Instagram templates. Quote posts, promos, carousels, stories. Fully editable.",17.00,"Templates","digital","SM",999,1),
            ("Freelance Proposal","8-page client proposal template. Cover, scope, pricing, terms, signature.",12.00,"Templates","digital","FP",999,0),
            ("Business Plan Workbook","Complete PDF workbook for planning and launching a new business.",15.00,"Guides","digital","BP",999,0),
            ("Complete Bundle","Every digital product in one download. Save $26 vs buying separately.",49.00,"Bundles","digital","BN",999,1),
            ("Solodeck Tee","Heavy cotton oversized tee. Minimal chest logo. Unisex sizing S-3XL.",35.00,"Apparel","physical","AP",100,1),
            ("Solodeck Hoodie","Classic pullover hoodie. Embroidered logo. Premium weight cotton blend.",58.00,"Apparel","physical","HD",50,0),
            ("Solodeck Cap","Structured 5-panel cap. Embroidered logo. One size fits most.",32.00,"Accessories","physical","CP",75,0),
            ("Motivational Poster","A3 bold typography print. Ships flat in protective sleeve. Ready to frame.",22.00,"Home","physical","PT",200,0),
            ("Entrepreneur Notebook","120 pages, matte cover, lay-flat binding. Your ideas deserve a proper home.",28.00,"Accessories","physical","NB",150,0),
        ]
        c.executemany("INSERT INTO products (name,description,price,category,type,image_label,stock,featured) VALUES(?,?,?,?,?,?,?,?)", rows)
    con.commit(); con.close()

init()

def get_cart(): return session.get("cart", {})
def cart_count(): return sum(get_cart().values())
def cart_total():
    con = db(); t = 0.0
    for pid, qty in get_cart().items():
        r = con.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()
        if r: t += r["price"] * qty
    con.close(); return round(t, 2)

@app.route("/")
def home():
    con = db()
    featured = con.execute("SELECT * FROM products WHERE featured=1 LIMIT 6").fetchall()
    con.close()
    return render_template("home.html", products=featured, cart_count=cart_count())

@app.route("/shop")
def shop():
    con = db()
    cat = request.args.get("category","all")
    typ = request.args.get("type","all")
    q = "SELECT * FROM products WHERE 1=1"; p = []
    if cat != "all": q += " AND category=?"; p.append(cat)
    if typ != "all": q += " AND type=?"; p.append(typ)
    q += " ORDER BY featured DESC, id"
    products = con.execute(q, p).fetchall()
    cats = con.execute("SELECT DISTINCT category FROM products").fetchall()
    con.close()
    return render_template("shop.html", products=products, categories=cats,
        active_cat=cat, active_type=typ, cart_count=cart_count())

@app.route("/product/<int:pid>")
def product(pid):
    con = db()
    item = con.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    related = con.execute("SELECT * FROM products WHERE category=? AND id!=? LIMIT 3", (item["category"], pid)).fetchall()
    con.close()
    return render_template("product.html", item=item, related=related, cart_count=cart_count())

@app.route("/cart")
def cart():
    items = []; con = db()
    for pid, qty in get_cart().items():
        r = con.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if r: items.append({"product": r, "qty": qty, "subtotal": round(r["price"]*qty, 2)})
    con.close()
    return render_template("cart.html", items=items, total=cart_total(), cart_count=cart_count())

@app.route("/cart/add/<int:pid>", methods=["POST"])
def add_to_cart(pid):
    cart = get_cart(); key = str(pid)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart; flash("Added to cart!", "success")
    return redirect(request.referrer or url_for("shop"))

@app.route("/cart/remove/<int:pid>")
def remove_from_cart(pid):
    cart = get_cart(); cart.pop(str(pid), None)
    session["cart"] = cart; return redirect(url_for("cart"))

@app.route("/cart/update", methods=["POST"])
def update_cart():
    cart = get_cart(); pid = str(request.form.get("pid")); qty = int(request.form.get("qty", 1))
    if qty <= 0: cart.pop(pid, None)
    else: cart[pid] = qty
    session["cart"] = cart; return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET","POST"])
def checkout():
    if not get_cart(): return redirect(url_for("shop"))
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        if not name or not email:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("checkout"))
        con = db(); items = []; total = 0.0
        for pid, qty in get_cart().items():
            r = con.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            if r: items.append({"name": r["name"], "qty": qty, "price": r["price"]}); total += r["price"]*qty
        con.execute("INSERT INTO orders (email,name,items,total,status) VALUES(?,?,?,?,'confirmed')",
            (email, name, json.dumps(items), round(total,2)))
        oid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.commit(); con.close()
        session["cart"] = {}
        session["last_order"] = {"id": oid, "name": name, "email": email, "total": round(total,2), "items": items}
        return redirect(url_for("order_confirm"))
    return render_template("checkout.html", total=cart_total(), cart_count=cart_count())

@app.route("/order/confirm")
def order_confirm():
    order = session.get("last_order")
    if not order: return redirect(url_for("home"))
    return render_template("confirm.html", order=order, cart_count=0)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email","").strip()
    if email:
        con = db()
        try:
            con.execute("INSERT INTO subscribers (email) VALUES(?)", (email,)); con.commit()
            flash("You're in! 15% off your first order coming your way.", "success")
        except sqlite3.IntegrityError:
            flash("You're already subscribed!", "info")
        con.close()
    return redirect(request.referrer or url_for("home"))

@app.route("/admin")
def admin():
    con = db()
    products = con.execute("SELECT * FROM products ORDER BY id").fetchall()
    orders = con.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 20").fetchall()
    subs = con.execute("SELECT COUNT(*) as count FROM subscribers").fetchone()
    rev = con.execute("SELECT SUM(total) as r FROM orders WHERE status='confirmed'").fetchone()
    con.close()
    return render_template("admin.html", products=products, orders=orders,
        sub_count=subs["count"], revenue=rev["r"] or 0.0, cart_count=cart_count())

@app.route("/admin/product/add", methods=["POST"])
def admin_add():
    con = db()
    con.execute("INSERT INTO products (name,description,price,category,type,image_label,stock,featured) VALUES(?,?,?,?,?,?,?,?)",(
        request.form["name"], request.form.get("description",""),
        float(request.form["price"]), request.form.get("category","General"),
        request.form.get("type","digital"), request.form.get("image_label","SD"),
        int(request.form.get("stock",999)), 1 if request.form.get("featured") else 0))
    con.commit(); con.close(); flash("Product added!","success")
    return redirect(url_for("admin"))

@app.route("/admin/product/delete/<int:pid>")
def admin_delete(pid):
    con = db(); con.execute("DELETE FROM products WHERE id=?", (pid,)); con.commit(); con.close()
    flash("Product deleted.","info"); return redirect(url_for("admin"))

@app.route("/admin/order/<int:oid>/status", methods=["POST"])
def order_status(oid):
    con = db(); con.execute("UPDATE orders SET status=? WHERE id=?", (request.form.get("status","pending"), oid))
    con.commit(); con.close(); return redirect(url_for("admin"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration – Render वर environment variable वापरा
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quntity = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()  # tables तयार करा

# Routes
@app.route("/")
def home():
    items = MenuItem.query.all()
    custom_order = ["TEA", "SANDWICH", "HOT COFFEE", "SIDES", "COLD COFFEE", "BURGER"]
    grouped_menu = {}
    for item in items:
        grouped_menu.setdefault(item.type, []).append(item)
    ordered_menu = {key: grouped_menu[key] for key in custom_order if key in grouped_menu}
    return render_template("index.html", menu=ordered_menu)

@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json()
    try:
        for item in data:
            menu_item = MenuItem.query.get(item["id"])
            if menu_item:
                menu_item.quntity = item["quntity"]
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500

@app.route("/bill")
def bill():
    items = MenuItem.query.filter(MenuItem.quntity > 0).all()
    subtotal = sum(item.price * item.quntity for item in items)
    gst = round(subtotal * 0.12, 2)
    discount = round(subtotal * 0.25, 2)
    total = round(subtotal + gst - discount, 2)
    return render_template("bill.html", items=items, subtotal=subtotal, gst=gst, discount=discount, total=total)

@app.route("/clear_orders", methods=["POST"])
def clear_orders():
    try:
        items = MenuItem.query.filter(MenuItem.quntity > 0).all()
        for item in items:
            item.quntity = 0
        db.session.commit()
        return "Cleared", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

# Production-ready run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

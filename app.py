from flask import Flask, request, jsonify, send_from_directory
import json
import re

app = Flask(__name__)

# Load product and order data
with open("data/products.json", "r") as f:
    products = json.load(f)

with open("data/orders.json", "r") as f:
    orders = json.load(f)

@app.route("/")
def home():
    return send_from_directory("static", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()

    if "refund" in user_message:
        return handle_refund(user_message)
    else:
        return get_product_info(user_message)

def handle_refund(message):
    match = re.search(r'order\s*id[:\-]?\s*(\d+)', message, re.IGNORECASE)
    if not match:
        return jsonify({"reply": "❓ Please provide your Order ID to process the refund."})

    order_id = int(match.group(1))

    matching_orders = [o for o in orders if int(o["order_id"]) == order_id]

    if not matching_orders:
        return jsonify({"reply": f"❌ Order ID {order_id} not found."})

    newly_refunded = []
    already_refunded = []
    too_old = []

    for item in matching_orders:
        if item["status"] == "refunded":
            already_refunded.append(item["product_name"])
        elif item["days_since_delivery"] > 7:
            too_old.append(item["product_name"])
        elif item["status"] == "delivered":
            item["status"] = "refunded"
            newly_refunded.append(item["product_name"])

    # Save updated orders
    with open("data/orders.json", "w") as f:
        json.dump(orders, f, indent=2)

    if not newly_refunded:
        reply_lines = [f"❌ No refundable items found in Order ID {order_id}."]
    if already_refunded:
        reply_lines.append(f"🔁 {len(already_refunded)} item(s) were already refunded.")
    if too_old:
        reply_lines.append(f"⏳ {len(too_old)} item(s) are too old for refund.")
    return jsonify({"reply": "<br>".join(reply_lines)})

# Construct success response
    reply_lines = [
        f"✅ Refunded {len(newly_refunded)} item(s) in Order ID {order_id}: " + ", ".join(newly_refunded)
    ]
    if already_refunded:
        reply_lines.append(f"🔁 {len(already_refunded)} item(s) were already refunded.")
    if too_old:
        reply_lines.append(f"⏳ {len(too_old)} item(s) are too old for refund.")

    return jsonify({"reply": "<br>".join(reply_lines)})


def get_product_info(message):
    for product in products:
        if product["name"].lower() in message:
            return jsonify({
                "reply": f"{product['name']} costs ₹{product['price']}. {product['description']}"
            })

    return jsonify({"reply": "Sorry, I couldn't find that product."})

if __name__ == "__main__":
    app.run(debug=True)

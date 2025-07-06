import json

with open("data/orders.json", "r") as f:
    orders = json.load(f)

# Keep only the first 200 entries
small_orders = orders[:200]

with open("data/orders.json", "w") as f:
    json.dump(small_orders, f, indent=2)

print("✅ Trimmed orders.json to first 200 entries.")

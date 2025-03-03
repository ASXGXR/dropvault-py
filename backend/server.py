from flask import Flask, jsonify, Response, request
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})  # Allow frontend access

# Get ebay orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        with open("C:/Users/44755/3507 Dropbox/Alex Sagar/WEBSITES/dropvault-py/backend/aliexpress/shipped_orders.json", "r", encoding="utf-8") as f:
            orders = json.load(f)

        # Use Response instead of jsonify to disable sorting
        return Response(json.dumps(orders, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Get ebay listings
@app.route('/api/ebay-listings', methods=['GET'])
def get_ebay_listings():
    try:
        with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\listings.json", "r", encoding="utf-8") as f:
            listings = json.load(f)

        return Response(json.dumps(listings, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Update aliexpress URLs
@app.route('/api/update-aliexpress', methods=['POST'])
def update_aliexpress():
    try:
        data = request.get_json() or {}
        item_id, new_url = data.get("item_id"), data.get("aliexpress_url")
        if not item_id or new_url is None:
            return jsonify({"error": "Invalid payload"}), 400

        listings_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\listings.json"
        with open(listings_path, "r", encoding="utf-8") as f:
            listings = json.load(f)

        for listing in listings:
            if listing.get("item_id") == item_id:
                listing["aliexpress_url"] = new_url
                break
        else:
            return jsonify({"error": "Listing not found"}), 404

        with open(listings_path, "w", encoding="utf-8") as f:
            json.dump(listings, f, indent=4, ensure_ascii=False)
        return jsonify({"success": True, "item_id": item_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
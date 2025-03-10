from flask import Flask, jsonify, Response, request
import json
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from anywhere (TEMPORARY for debugging)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

# If you want to limit access, use this instead:
# CORS(app, resources={r"/api/*": {"origins": ["http://192.168.0.70:5500", "http://82.42.112.27:5500"]}})

# Get ebay orders
@app.route('/api/ebay-orders', methods=['GET'])
def get_orders():
    try:
        with open("C:/Users/44755/3507 Dropbox/Alex Sagar/WEBSITES/dropvault-py/backend/aliexpress/shipped_orders.json", "r", encoding="utf-8") as f:
            orders = json.load(f)

        # Use Response instead of jsonify to disable sorting
        return Response(json.dumps(orders, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Get shipped orders
@app.route('/api/shipped-orders', methods=['GET'])
def get_shipped_orders():
    try:
        with open("C:/Users/44755/3507 Dropbox/Alex Sagar/WEBSITES/dropvault-py/backend/aliexpress/shipped_orders.json", "r", encoding="utf-8") as f:
            shipped_orders = json.load(f)

        return Response(json.dumps(shipped_orders, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
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
    
# Update ali-value for variants
@app.route('/api/update-variant', methods=['POST'])
def update_variant():
    try:
        data = request.get_json() or {}
        item_id, variant_title, new_value = data.get("listingId"), data.get("variantTitle"), data.get("value")
        if not item_id or new_value is None or variant_title is None:
            return jsonify({"error": "Invalid payload"}), 400

        path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\listings.json"
        with open(path, "r", encoding="utf-8") as f:
            listings = json.load(f)

        for listing in listings:
            if listing.get("item_id") != item_id:
                continue
            if variant_title == "Default" and (("variations" not in listing) or not listing["variations"]):
                listing["ali-value"] = new_value
            elif "variations" in listing:
                for options in listing["variations"].values():
                    for option in options:
                        if option.get("value") == variant_title:
                            option["ali-value"] = new_value
            break
        else:
            return jsonify({"error": "Listing not found"}), 404

        with open(path, "w", encoding="utf-8") as f:
            json.dump(listings, f, indent=4, ensure_ascii=False)

        return jsonify({"success": True, "item_id": item_id, "variant_title": variant_title, "new_value": new_value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
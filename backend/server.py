from flask import Flask, jsonify, Response, request, send_from_directory
from flask_cors import CORS
import json
import os  # Add this import for file existence checks

app = Flask(__name__)

# Allow requests from anywhere (TEMPORARY for debugging)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Base roots
root_dir = os.getcwd()  # Get current working directory
aliexpress_dir = rf"{root_dir}\backend\aliexpress"
ebay_dir = rf"{root_dir}\backend\ebay"

# Individual files
shipped_orders_path = rf"{aliexpress_dir}\shipped_orders.json"
failed_shipments_path = rf"{aliexpress_dir}\failed_shipments.json"
shipping_screenshots_dir = rf"{aliexpress_dir}\shipping_screenshots"
listings_path = rf"{ebay_dir}\listings.json"

# Get ebay orders
@app.route('/api/ebay-orders', methods=['GET'])
def get_orders():
    try:
        with open(shipped_orders_path, "r", encoding="utf-8") as f:
            orders = json.load(f)

        # Use Response instead of jsonify to disable sorting
        return Response(json.dumps(orders, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Get shipped orders
@app.route('/api/shipped-orders', methods=['GET'])
def get_shipped_orders():
    try:
        with open(shipped_orders_path, "r", encoding="utf-8") as f:
            shipped_orders = json.load(f)

        return Response(json.dumps(shipped_orders, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    
# Serve shipping screenshots
@app.route('/api/shipping-screenshot/<path:filename>', methods=['GET'])
def get_shipping_screenshot(filename):
    return send_from_directory(shipping_screenshots_dir, filename)

# Get ebay listings
@app.route('/api/ebay-listings', methods=['GET'])
def get_ebay_listings():
    try:
        with open(listings_path, "r", encoding="utf-8") as f:
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
        with open(listings_path, "r", encoding="utf-8") as f:
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
        with open(listings_path, "w", encoding="utf-8") as f:
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
    
# Get failed shipments
@app.route('/api/failed-shipments', methods=['GET'])
def get_failed_shipments():
    try:
        with open(failed_shipments_path, "r", encoding="utf-8") as f:
            failed_shipments = json.load(f)
        return Response(json.dumps(failed_shipments, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Retry failed order
@app.route('/api/retry-order', methods=['POST'])
def retry_failed_order():
    data = request.get_json() or {}
    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"error": "Missing item_id"}), 400
    with open(failed_shipments_path, "r", encoding="utf-8") as f:
        shipments = json.load(f)
    for shipment in shipments:
        if shipment.get("item_id") == item_id:
            shipment.update({k: v for k, v in data.items() if k in shipment})
            shipment["retryOrder"] = True
            break
    else:
        return jsonify({"error": "Item not found"}), 404
    with open(failed_shipments_path, "w", encoding="utf-8") as f:
        json.dump(shipments, f, indent=4, ensure_ascii=False)
    return jsonify({"success": True, "item_id": item_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
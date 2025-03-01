from flask import Flask, jsonify, Response
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})  # Allow frontend access

@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        with open("C:/Users/44755/3507 Dropbox/Alex Sagar/WEBSITES/dropvault-py/backend/aliexpress/shipped_orders.json", "r", encoding="utf-8") as f:
            orders = json.load(f)

        # Use Response instead of jsonify to disable sorting
        return Response(json.dumps(orders, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    
@app.route('/api/ebay-listings', methods=['GET'])
def get_ebay_listings():
    try:
        with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\ebay_listings_raw.json", "r", encoding="utf-8") as f:
            listings = json.load(f)

        return Response(json.dumps(listings, ensure_ascii=False, indent=4, sort_keys=False), mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
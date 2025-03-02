from flask import Flask, jsonify, Response, request
import subprocess
import sys
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

# Search the web
@app.route('/api/search-web', methods=['POST'])
def run_search():
    data = request.get_json()
    title = data.get("title")
    if not title:
        return jsonify({"error": "No title provided"}), 400

    try:
        # Run the external Python file with the title argument.
        result = subprocess.run(
            [sys.executable, r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\search-web.py", title],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
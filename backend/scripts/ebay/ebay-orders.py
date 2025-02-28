from datetime import datetime, timedelta
import requests
import json
import time

# Check 1 hour passed - refresh access token
hour_pass = 1
current_time = datetime.now()
token_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\scripts\ebay\a_token_refresh_time.txt"
script_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\scripts\ebay\refresh-access-token.py"

with open(token_file, "r") as file:
    last_refresh_time = datetime.strptime(file.read().strip(), "%Y-%m-%d %H:%M:%S")
if current_time > last_refresh_time + timedelta(hours=hour_pass):
    print("Refreshing access token...")
    with open(script_file, "r") as script:
        exec(script.read(), globals())  # Executes within the same process
time.sleep(2)

# eBay API credentials
EBAY_ACCESS_TOKEN = open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\scripts\ebay\a_token.txt").read().strip()

# eBay Orders API endpoint
EBAY_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order"

# Headers with authentication
headers = {
    "Authorization": f"Bearer {EBAY_ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Request parameters (fetching last 10 orders)
params = {
    "limit": 10,
    "filter": "orderfulfillmentstatus:{NOT_STARTED|IN_PROGRESS}"
}

# Make API request
response = requests.get(EBAY_ORDERS_URL, headers=headers, params=params)

# Process response
if response.status_code == 200:
    orders = response.json()

    # Save orders to ebay_orders.json
    with open("ebay_orders.json", "w") as f:
        json.dump(orders, f, indent=4)

    print("Orders saved to ebay_orders.json")
else:
    print(f"Error: {response.status_code}, {response.text}")
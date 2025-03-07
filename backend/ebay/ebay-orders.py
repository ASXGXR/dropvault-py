from ebaysdk.trading import Connection as Trading
from datetime import datetime, timedelta
import requests
import json
import time

#######################
##  EBAY API ACCESS  ##
#######################

# Check 1 hour passed - refresh access token
hour_pass = 1
current_time = datetime.now()
token_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\a_token_refresh_time.txt"
script_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\refresh-access-token.py"

with open(token_file, "r") as file:
    last_refresh_time = datetime.strptime(file.read().strip(), "%Y-%m-%d %H:%M:%S")
if current_time > last_refresh_time + timedelta(hours=hour_pass):
    print("Refreshing access token...")
    with open(script_file, "r") as script:
        exec(script.read(), globals())
    time.sleep(2)

# eBay API credentials
EBAY_ACCESS_TOKEN = open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\a_token.txt").read().strip()

####################
##  GET LISTINGS  ##
####################

try:
    EBAY_APP_ID = 'AlexSaga-DropVaul-PRD-5deb947bc-5f49e26a'
    EBAY_CERT_ID = 'PRD-deb947bc0570-5952-4a60-963f-ef77'
    EBAY_DEV_ID = 'f08e4a91-97f3-4c8f-a921-88b2b20b6610'

    api = Trading(appid=EBAY_APP_ID,
                  certid=EBAY_CERT_ID,
                  devid=EBAY_DEV_ID,
                  token=EBAY_ACCESS_TOKEN,
                  config_file=None)

    page = 1
    all_listings = []

    while True:
        response = api.execute('GetMyeBaySelling', {
            'ActiveList': {
                'Include': True,
                'Pagination': {
                    'EntriesPerPage': 100,
                    'PageNumber': page
                }
            }
        })
        data = response.dict()
        items = data.get('ActiveList', {}).get('ItemArray', {}).get('Item', [])
        if not items:
            break
        if isinstance(items, dict):
            items = [items]
        all_listings.extend(items)
        total_pages = int(data.get('ActiveList', {}).get('PaginationResult', {}).get('TotalNumberOfPages', 1))
        if page >= total_pages:
            break
        page += 1

    with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\raw_listings.json", 'w') as outfile:
        json.dump(all_listings, outfile, indent=4)

    print(f"{len(all_listings)} listings retrieved.")

except Exception as e:
    print(f"Unable to retrieve eBay listings: {e}")


##  PARSE  ##
try:
    listings_json_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\listings.json"
    with open(listings_json_path) as f:
        try:
            existing_aliexpress = {item.get("item_id", ""): item.get("aliexpress_url", "") for item in json.load(f)}
        except json.JSONDecodeError:
            existing_aliexpress = {}

    filtered_listings = []
    for listing in reversed(all_listings):
        item_id = listing.get("ItemID", "")
        filtered = {
            "item_id": item_id,
            "title": listing.get("Title", ""),
            "item_url": listing.get("ListingDetails", {}).get("ViewItemURL", ""),
            "price": listing.get("BuyItNowPrice", {}).get("value", ""),
            "image_url": listing.get("PictureDetails", {}).get("GalleryURL", ""),
            "aliexpress_url": existing_aliexpress.get(item_id, ""),
            "variations": {}
        }
        variations = listing.get("Variations", {}).get("Variation", [])
        if isinstance(variations, dict):
            variations = [variations]
        for var in variations:
            specifics = var.get("VariationSpecifics", {}).get("NameValueList", [])
            if isinstance(specifics, dict):
                specifics = [specifics]
            var_price = var.get("StartPrice", {}).get("value", "")
            for s in specifics:
                if "Name" in s and "Value" in s:
                    filtered["variations"].setdefault(s["Name"], []).append({
                        "value": s["Value"],
                        "price": var_price,
                    })
        filtered_listings.append(filtered)

    with open(listings_json_path, 'w') as outfile:
        json.dump(filtered_listings, outfile, indent=4)
except Exception as e:
    print(f"Unable to filter eBay listings: {e}")


######################
##  GETTING ORDERS  ##
######################

EBAY_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order"
headers = {
    "Authorization": f"Bearer {EBAY_ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
params = {
    "limit": 10,
    "filter": "orderfulfillmentstatus:{NOT_STARTED|IN_PROGRESS}"
}
response = requests.get(EBAY_ORDERS_URL, headers=headers, params=params)
if response.status_code == 200:
    orders = response.json()
    orders_json_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\ebay_orders.json"
    with open(orders_json_path, "w") as f:
        json.dump(orders, f, indent=4)
    order_count = len(orders.get("orders", []))
    print(f"{order_count} orders received.")
else:
    print(f"Error: {response.status_code}, {response.text}")
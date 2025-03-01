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
        exec(script.read(), globals())  # Executes within the same process
    time.sleep(2)  # Wait for token to refresh

# eBay API credentials
EBAY_ACCESS_TOKEN = open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\a_token.txt").read().strip()



######################
##  GETTING ORDERS  ##
######################


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
    with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\ebay_orders.json", "w") as f:
        json.dump(orders, f, indent=4)

    print("Orders received from eBay.")
else:
    print(f"Error: {response.status_code}, {response.text}")



########################
##  GETTING LISTINGS  ##
########################


try:
    # eBay credentials
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
        # Ensure items is a list
        if isinstance(items, dict):
            items = [items]
        all_listings.extend(items)
        
        total_pages = int(data.get('ActiveList', {}).get('PaginationResult', {}).get('TotalNumberOfPages', 1))
        if page >= total_pages:
            break
        page += 1

    with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\ebay_listings_raw.json", 'w') as outfile:
        json.dump(all_listings, outfile, indent=4)

    print(f"Retrieved {len(all_listings)} listings.")


except Exception as e:
    print(f"Unable to retrieve eBay listings: {e}")
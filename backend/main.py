import os
import time
import json
import pyautogui  # Import pyautogui for mouse position tracking
from ebay.get_access_token import getAccessToken
from ebay.ebay_listings import getListings
from ebay.ebay_orders import getOrders
from aliexpress.ali_order import makeAliOrder
from aliexpress.fix_shipped_orders import compress_old_orders

# --- File Paths  ---
root_dir = os.getcwd()  # Get current working directory
ebay_dir = rf"{root_dir}\backend\ebay"

# --- Initial Setup ---
print("**Starting up..")  # Show startup message
debug = False           # Debug mode toggle (False = off)
orders_printed = False  # Track if orders summary has been printed
last_time_printed = time.time()  # Last time the clock was printed
minute_gap = 10         # Minutes to wait between each full cycle

# --- Main Loop (runs forever) ---
while True:
    start_time = time.time()  # Records when cycle started

    # Print current time every 2 hours
    if start_time - last_time_printed >= 7200:
        print(f"🕒  Current Time: {time.strftime('%d-%m-%Y %H:%M:%S')}")
        last_time_printed = start_time

    # --- STEP 1: Get eBay Access Token ---
    access_token = getAccessToken()

    # --- STEP 2: Get eBay Listings and Orders ---
    getListings(access_token, debug)        # Download current listings
    orders = getOrders(access_token, debug) # Download recent orders

    # --- STEP 3: Print summary of orders (only once after starting) ---
    if not orders_printed:
        print(f"**{len(orders)} Orders Received & Parsed")
        print("\n" + "=" * 36)
        print("🔄  DropVault Automation Started")
        print("=" * 36 + "\n")
        orders_printed = True

    # --- STEP 4: Process each order (send to AliExpress script) ---
    for order in orders:
        makeAliOrder(order) # Run AliExpress order script

    # --- STEP 5: Wait until next run ---
    initial_position = pyautogui.position()
    while (time.time() - start_time) < (minute_gap * 60):

        # Pause if mouse moves
        if pyautogui.position() != initial_position:
            print("⏸️  Script Paused. Keep mouse still to resume.")
            while True:
                initial_position = pyautogui.position()
                time.sleep(180) # Wait for 3 minutes
                if pyautogui.position() == initial_position:
                    break
            print("▶️  Resuming Script...\n")

        # Check for retry orders
        try:
            path = rf"{root_dir}\backend\aliexpress\failed_shipments.json"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    shipments = json.load(f)

                for shipment in shipments:
                    if shipment.get("retryOrder"):
                        print(f"🔁 Retrying: {shipment['item_title']}")
                        # Make sure order only tried once
                        shipment["retryOrder"] = False
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(shipments, f, indent=4, ensure_ascii=False)
                        # Make ali order
                        makeAliOrder(shipment)
        except Exception as e:
            print("⚠️  Failed to process retry orders:", e)

        time.sleep(5)
    
    # --- STEP 6: Clean up old orders ---
    compress_old_orders()
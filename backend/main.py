import json
import time
from ebay.get_access_token import getAccessToken
from ebay.ebay_listings import getListings
from ebay.ebay_orders import getOrders
from aliexpress.ali_order import makeAliOrder

# --- File Paths  ---
ebay_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay"
pause_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\pause.txt"

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

    # --- STEP 5: Wait until next run, but check pause.txt file ---
    while (time.time() - start_time) < (minute_gap * 60):
        with open(pause_dir, "r") as f:
            if f.read().strip():  # If pause.txt has content, pause script
                print("⏸️  Script Paused. Remove contents of pause.txt to continue.")
                # Stay paused until pause.txt is cleared
                while True:
                    time.sleep(5)  # Check pause.txt every 5 seconds
                    with open(pause_dir, "r") as pause_file:
                        if not pause_file.read().strip():  # If pause.txt is empty, resume
                            print("▶️  Resuming Script...\n")
                            break
        time.sleep(5)  # Short delay to prevent overloading the CPU